from django.http import HttpResponse
from io import BytesIO, StringIO
from typing import Optional
from django.forms import ValidationError
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import validate_email
from rest_framework import status, request, response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import BasePermission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ..views.base_views import BaseView
from api.models import Event, Player, Results
from ..utils import handle_400_error
from ..serializers import PlayerSerializer, UploadFileSerializer, PlayerResultsSerializer, PlayerLoginSerializer
from ..swagger import Errors, manual_parameter_event_id
from ..permissions import assign_permissions
import pandas as pd
import chardet
import os


class PlayersPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return request.user.has_perm('api.view_player_event', obj)
        if request.method == 'POST':
            return request.user.has_perm('api.add_player_event', obj)
        if request.method == 'PUT':
            return request.user.has_perm('api.change_player_event', obj)
        if request.method == 'DELETE':
            return request.user.has_perm('api.delete_player_event', obj)
        return True


class PlayersView(BaseView):

    permission_classes = [IsAuthenticated, PlayersPermission]

    @ swagger_auto_schema(security=[{'Bearer': []}],
                          tags=['player'],
                          operation_description='Retorna todos os jogadores de um evento.',
                          operation_summary='Retorna todos os jogadores de um evento.',
                          manual_parameters=manual_parameter_event_id,
                          responses={200: openapi.Response(200, PlayerSerializer), **Errors([400]).retrieve_erros()})
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        """ Retorna todos os jogadores de um evento."""
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)

        players = Player.objects.filter(event=event)
        if not players:
            return response.Response(status=status.HTTP_200_OK, data=['Nenhum jogador encontrado!'])
        players_list = []
        for player in players:
            players_list.append(player)

        data = PlayerSerializer(players_list, many=True).data

        return response.Response(status=status.HTTP_200_OK, data=data)

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        tags=['player'],
        operation_description="""Realiza o login de um jogador no evento através do email fornecido na inscrição.
        Para um jogador entrar no evento, ele deve informar o email que foi utilizado na inscrição e o token de jogador fornecido pelo administrador do evento.
        """,
        operation_summary='Realiza o login de um jogador no evento.',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email do jogador'), 'join_token': openapi.Schema(
            type=openapi.TYPE_STRING, description='Token do evento')}, required=['email', 'join_token']),
        responses={200: openapi.Response(
            200, PlayerLoginSerializer), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """ Adiciona um jogador ao evento através do email fornecido na inscirção."""
        if 'email' not in request.data or 'join_token' not in request.data:
            return handle_400_error('Email e token são obrigatórios!')
        email = request.data['email']
        join_token = request.data['join_token']
        join_token = join_token.strip()
        if not email or not join_token:
            return handle_400_error('Email e token são obrigatórios!')
        event = Event.objects.filter(join_token=join_token).first()
        if not event:
            return handle_400_error('Evento não encontrado!')
        player = Player.objects.filter(
            registration_email=email, event=event).first()
        if not player:
            return handle_400_error('Jogador não encontrado!')
        if player.user is None:
            player.user = request.user
        elif player.user != request.user:
            return handle_400_error("""Jogador já está associado a outro usuário!
                                    Se isso é um erro, entre em contato com o administrador do evento.""")
        group = Group.objects.get(name='player')
        assign_permissions(request.user, group, event)
        player.is_present = True
        player.save()
        request.user.events.add(event)
        request.user.save()
        data = PlayerLoginSerializer(player).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    @swagger_auto_schema(
        tags=['player'],
        security=[{'Bearer': []}],
        operation_summary='Deleta um jogador do evento.',
        operation_description='Deleta um jogador do evento através do ID fornecido no request_body.  Apenas o administrador do evento pode realizar essa ação.',
        manual_parameters=manual_parameter_event_id,
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'id': openapi.Schema(
            type=openapi.TYPE_INTEGER, description='ID do jogador')}, required=['id']),
        responses={200: openapi.Response(
            200), **Errors([400]).retrieve_erros()}
    )
    def delete(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Deleta um jogador do evento."""
        if 'id' not in request.data:
            return handle_400_error('ID do jogador é obrigatório!')
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        player_id = request.data.get('id')
        if not player_id:
            return handle_400_error('ID do jogador é obrigatório!')
        player = Player.objects.filter(id=player_id, event=event).first()
        if not player:
            return handle_400_error('Jogador não encontrado!')
        player.delete()
        return response.Response(status=status.HTTP_200_OK, data='Jogador deletado com sucesso!')

    @swagger_auto_schema(
        tags=['player'],
        operation_description="""Edita os dados de um jogador no evento.
        É permitido editar o **nome completo, nome social, email do jogador, is_imortal e is_present**.
        **Deve ser fornecido no request_body o email atual do jogador** e os campos que deseja alterar:
        - registration_email: Email atual do jogador
        - id: ID do jogador
        - social_name: Nome social do jogador
        - new_email: Novo email do jogador
        - is_imortal: Jogador é imortal
        - is_present: Jogador está presente no evento
        - clear_user: Limpar usuário do jogador, caso deseje remover o usuário do jogador.
        Note que as chaves do request_body devem ser passadas, porém o valor pode ser vazio, **exceto dos campos is_imortal e is_present, que devem ser bools**.
        """,
        operation_summary='Edita os dados de um jogador no evento.',
        manual_parameters=manual_parameter_event_id,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador', example=1),
                'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome completo do jogador', example='João da Silva'),
                'social_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome social do jogador', example='Joana Silva'),
                'new_email': openapi.Schema(type=openapi.TYPE_STRING, description='Novo email do jogador', example='new@email.com'),
                'is_imortal': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Jogador é imortal', example=False),
                'is_present': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Jogador está presente no evento', example=True),
                'clear_user': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Limpar usuário do jogador', example=False),
            },
            required=['registration_email']
        ),
        responses={200: openapi.Response(
            200, PlayerSerializer), **Errors([400]).retrieve_erros()}
    )
    def put(self, request: request.Request, *args, **kwargs):
        required_fields = ['id', 'full_name',
                           'social_name', 'new_email', 'is_imortal', 'is_present']
        if request.data is None or not all(field in request.data for field in required_fields):
            return handle_400_error('Dados Inválidos!')
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        if event not in request.user.events.all():
            return handle_400_error('Usuário não tem permissão para acessar este evento!')
        self.check_object_permissions(request, event)

        player_id = request.data['id']
        if not player_id:
            return handle_400_error('ID do jogador é obrigatório!')
        player = Player.objects.filter(id=player_id, event=event).first()
        if not player:
            return handle_400_error('Jogador não encontrado!')

        full_name = request.data['full_name']
        social_name = request.data['social_name']
        new_email = request.data['new_email']
        is_imortal = request.data['is_imortal']
        is_present = request.data['is_present']
        clear_user = request.data.get('clear_user', False)
        if not isinstance(is_imortal, bool) or not isinstance(is_present, bool):
            return handle_400_error('is_imortal e is_present devem ser booleanos!')
        player.is_imortal = is_imortal
        player.is_present = is_present
        if full_name:
            full_name = full_name.strip().lower()
            for word in full_name.split():
                full_name = full_name.replace(word, word.capitalize())
            player.full_name = full_name
        if social_name:
            social_name = social_name.strip().lower()
            for word in social_name.split():
                social_name = social_name.replace(word, word.capitalize())
            player.social_name = social_name
        if new_email:
            new_email = new_email.strip()
            try:
                validate_email(new_email)
            except Exception:
                return handle_400_error('Email inválido!')
            player.registration_email = new_email
        if clear_user:
            player.user = None
            player.save()
            return response.Response(status=status.HTTP_200_OK, data='Jogador editado com sucesso. Usuário removido do jogador!')
        player.save()
        return response.Response(status=status.HTTP_200_OK, data='Jogador editado com sucesso!')


class GetPlayerResults(BaseView):
    permission_classes = [IsAuthenticated, PlayersPermission]

    @swagger_auto_schema(
        tags=['results'],
        security=[{'Bearer': []}],
        operation_summary='Retorna o resultado a pontuação do usuário PLAYER logado.',
        operation_description="""Retorna o resultado de pontuação do jogador atual do usuário logado.
        Note que o resultado de pontuação só é retornado se o administrador do evento tiver publicado os resultados.
        **Este resultado representa a pontuação individual do jogador no evento.**
        """,
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(200, PlayerResultsSerializer), **Errors([400]).retrieve_erros()})
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        """ Retorna o resultado de pontuação do jogador atual do usuário logado."""
        try:
            event = self.get_event()
        except ValidationError as e:
            return handle_400_error(str(e))
        if not event.is_imortal_results_published:
            return response.Response(status=status.HTTP_403_FORBIDDEN, data='Resultados de pontuação não publicados!')
        self.check_object_permissions(request, event)
        player = Player.objects.filter(event=event, user=request.user).first()
        if not player:
            return handle_400_error('Jogador não encontrado!')

        data = PlayerResultsSerializer(player).data

        return response.Response(status=status.HTTP_200_OK, data=data)


class AddPlayersExcel(BaseView):
    permission_classes = [IsAuthenticated, PlayersPermission]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=['player'],
        operation_description='Adiciona os jogadores ao evento através do excel fornecido pelo administrador com os participantes do evento.',
        operation_summary='Adiciona multiplos jogadores ao evento.',
        manual_parameters=manual_parameter_event_id,
        request_body=UploadFileSerializer,
        responses={201: openapi.Response(
            201), **Errors([400]).retrieve_erros()})
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Adiciona os jogadores ao evento através do excel
        forncecido pelo administrador com os participantes do evento."""
        try:
            event = self.get_event()
        except ValidationError as e:
            return handle_400_error(str(e))

        self.check_object_permissions(self.request, event)

        try:
            excel_file = self.get_excel_file()
        except ValidationError as e:
            return handle_400_error(str(e))

        # Obtém a última extensão do arquivo
        extension = os.path.splitext(excel_file.name)[-1].lower().strip('.')
        # Cria o DataFrame usando a extensão correta
        df = self.createData(extension=extension, file=excel_file)
        if df is None:
            return handle_400_error('Arquivo inválido!')
        try:
            errors_count, players_count = self.create_players(
                df=df, event=event)
        except Exception as e:
            return handle_400_error(str(e))
        if errors_count > 0 and errors_count < players_count:
            return response.Response(status=status.HTTP_201_CREATED, data={
                'message': 'Jogadores adicionados com sucesso!',
                'errors': f'{errors_count} jogadores não foram adicionados devido a e-mail inválido. Verfique os e-mails dos jogadores e tente novamente.'
            })
        elif errors_count >= players_count:
            return handle_400_error('Nenhum jogador adicionado! Verifique os e-mails do arquivo!')
        return response.Response(status=status.HTTP_201_CREATED, data='Jogadores adicionados com sucesso!')

    def create_players(self, df: pd.DataFrame, event: Event) -> tuple[int, int]:
        process_data = ['nome completo', 'e-mail']
        df.columns = df.columns.str.strip().str.lower()
        # Verificar se as colunas necessárias estão presentes
        missing_columns = [
            col for col in process_data if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"ERRO - Colunas ausentes no arquivo: {', '.join(missing_columns)}")
        df_needed = df[process_data]

        players_count = 0
        errors_count = 0
        for i, line in df_needed.iterrows():
            name = line['nome completo']
            email = line['e-mail']
            name, email = self.treat_name_and_email_excel(name, email)
            players_count += 1
            try:
                validate_email(email)
            except ValidationError:
                errors_count += 1
                continue
            player, created = Player.objects.get_or_create(
                registration_email=email, event=event)
            player.full_name = name
            player.is_present = True
            player.save()
        return errors_count, players_count

    def createData(self, extension, file) -> Optional[pd.DataFrame]:
        data = None
        if extension == 'csv':
            csv_data, encoding = self.treat_csv(file)
            delimiter = self.get_delimiter(csv_data)
            data = pd.read_csv(csv_data, header=0,
                               encoding=encoding, delimiter=delimiter)

        elif extension == 'xlsx' or extension == 'xls':
            data = pd.read_excel(file)
        return data

    def get_excel_file(self):
        excel_file = self.request.data['file']
        if not isinstance(excel_file, UploadedFile):
            raise ValidationError('Arquivo inválido!')
        if not excel_file:
            raise ValidationError('Arquivo não encontrado!')
        if not excel_file.name:
            raise ValidationError('Arquivo inválido!')
        return excel_file


class AddSinglePlayer(BaseView):
    permission_classes = [IsAuthenticated, PlayersPermission]

    @ swagger_auto_schema(
        tags=['player'],
        operation_description="""Adiciona um jogador manualmente ao evento.
        Deve ser fornecido o nome completo do jogador como _request body_ e o ID do evento como _manual parameter_. Nome social e email são opcionais.

        Retorno: Retorna o objeto do jogador criado no evento para a utilização imediata no front-end.
        """,
        operation_summary='Adiciona um jogador manualmente ao evento.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome completo do jogador', example='João da Silva'),
                'social_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome social do jogador', example='Joana Silva'),
                'registration_email': openapi.Schema(type=openapi.TYPE_STRING, description='Email do jogador', example='joao@gmail.com'),
                'is_imortal': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Jogador é imortal', example=False)},
        ),
        required=['full_name'],
        manual_parameters=manual_parameter_event_id,
        responses={201: openapi.Response(
            201, PlayerSerializer), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Adiciona um jogador manualmente ao evento."""
        required_fields = ['full_name',
                           'registration_email', 'social_name', 'is_imortal']
        if request.data is None or not all(field in request.data for field in required_fields):
            return handle_400_error('Dados Inválidos!')
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        full_name = request.data['full_name']
        social_name = request.data['social_name']
        email = request.data['registration_email']
        is_imortal = request.data['is_imortal']
        if not full_name:
            return handle_400_error('Nome completo é obrigatório para criar um jogador!')
        full_name = full_name.strip()
        for word in full_name.split():
            full_name = full_name.replace(word, word.capitalize())
        if social_name:
            social_name = social_name.strip()
            for word in social_name.split():
                social_name = social_name.replace(word, word.capitalize())
        email = email.strip() if email else None
        try:
            validate_email(email)
        except Exception:
            return handle_400_error('Email inválido!')
        player, created = Player.objects.get_or_create(
            event=event, registration_email=email)
        if not created:
            return handle_400_error('Já existe um jogador cadastrado com esse email!')
        player.full_name = full_name
        player.social_name = social_name
        player.is_imortal = is_imortal
        player.is_present = True
        player.save()
        data = PlayerSerializer(player).data
        return response.Response(status=status.HTTP_201_CREATED, data=data)


class DeleteAllPlayers(BaseView):
    permission_classes = [IsAuthenticated, PlayersPermission]

    @swagger_auto_schema(
        tags=['player'],
        operation_description='Deleta todos os jogadores do evento.',
        operation_summary='Deleta todos os jogadores do evento. Apenas o administrador do evento pode realizar essa ação.',
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(
            200), **Errors([400]).retrieve_erros()}
    )
    def delete(self, request: request.Request, *args, **kwargs):
        """Deleta todos os jogadores do evento."""
        try:
            event = self.get_event()
        except ValidationError as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        players = Player.objects.filter(event=event)
        players.delete()
        return response.Response(status=status.HTTP_200_OK, data='Todos os jogadores deletados com sucesso!')


class GetNotImortalPlayers(BaseView):
    permission_classes = [IsAuthenticated, PlayersPermission]

    @swagger_auto_schema(
        tags=['player'],
        operation_description="""Retorna todos os jogadores não imortais do evento, ou seja **jogadores que ainda estão disputando as chaves princiapais do RRDD**. """,
        operation_summary="""Retorna todos os jogadores NÃO imortais do evento (classficados nas chaves). """,
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(
            200, PlayerSerializer), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        """ Retorna todos os jogadores não imortais do evento."""
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)

        players = Player.objects.filter(event=event, is_imortal=False)
        players_list = []
        for player in players:
            players_list.append(player)

        data = PlayerSerializer(players_list, many=True).data

        return response.Response(status=status.HTTP_200_OK, data=data)


class ExportPlayersView(BaseView):
    permission_classes = [IsAuthenticated, PlayersPermission]

    @swagger_auto_schema(
        tags=['player'],
        operation_description="""Exporta os jogadores classificados nas chaves do evento em um arquivo Excel.
        O arquivo Excel contém as informações de **Nome Completo, Email e Nome Social** dos jogadores classificados nas chaves.
        """,
        operation_summary='Exporta os jogadores classificados nas chaves do evento em um arquivo Excel.',
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(
            description='Arquivo Excel gerado com sucesso',
            content={'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {}}), **Errors([400]).retrieve_erros()})
    def get(self, request, *args, **kwargs):
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))

        self.check_object_permissions(request, event)

        players = Player.objects.filter(
            event=event, is_imortal=False, total_score__gt=0)
        print(players)
        if not players:
            return handle_400_error('Nenhum jogador encontrado!')

        # Gera o arquivo Excel
        excel_file = self.generate_excel(players=players)

        # Cria a resposta HTTP com o arquivo Excel
        response = HttpResponse(
            excel_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=jogadores_classificados.xlsx'

        return response

    def generate_excel(self, players):
        # Cria um DataFrame com os dados dos jogadores
        data = {
            'Nome Completo': [player.full_name for player in players],
            'Email': [player.registration_email for player in players],
            'Nome Social': [player.social_name for player in players],
        }
        df = pd.DataFrame(data)

        # Salva o DataFrame em um buffer de memória
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False,
                        sheet_name='Jogadores Classificados')

        # Move o ponteiro do buffer para o início
        buffer.seek(0)

        return buffer
