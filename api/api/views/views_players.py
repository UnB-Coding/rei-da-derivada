from io import StringIO
from typing import Optional
from django.forms import ValidationError
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import UploadedFile
from rest_framework import status, request, response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import BasePermission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ..views.base_views import BaseView
from api.models import Event, Player
from ..utils import handle_400_error
from ..serializers import PlayerSerializer, UploadFileSerializer, PlayerResultsSerializer, PlayerLoginSerializer
from ..swagger import Errors, manual_parameter_event_id
from ..permissions import assign_permissions
import pandas as pd


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
            event = self.get_object()
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
        operation_description="""Realiza o login de um jogador no    evento através do email fornecido na inscrição.
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
        player.save()
        request.user.events.add(event)
        request.user.save()
        data = PlayerLoginSerializer(player).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    def get_object(self) -> Event:
        if 'event_id' not in self.request.query_params:  # type: ignore
            raise ValidationError('Dados inválidos!')

        event_id = self.request.query_params.get('event_id')  # type: ignore
        if not event_id:
            raise ValidationError('event_id é obrigatório!')
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise ValidationError('Evento não encontrado!')
        return event


class GetPlayerResults(BaseView):
    permission_classes = [IsAuthenticated, PlayersPermission]

    @swagger_auto_schema(
        tags=['player'],
        security=[{'Bearer': []}],
        operation_summary='Retorna o resultado a pontuação do jogador',
        operation_description='Retorna o resultado de pontuação do jogador atual do usuário logado.',
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(200, PlayerResultsSerializer), **Errors([400]).retrieve_erros()})
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        """ Retorna o resultado de pontuação do jogador atual do usuário logado."""
        try:
            event = self.get_object()
        except ValidationError as e:
            return handle_400_error(str(e))
        if not event.is_results_published():
            return response.Response(status=status.HTTP_403_FORBIDDEN, data='Resultados não publicados!')
        self.check_object_permissions(request, event)
        player = Player.objects.filter(event=event, user=request.user).first()
        if not player:
            return handle_400_error('Jogador não encontrado!')

        data = PlayerResultsSerializer(player).data

        return response.Response(status=status.HTTP_200_OK, data=data)

    def get_object(self) -> Event:
        if 'event_id' not in self.request.query_params:  # type: ignore
            raise ValidationError('Dados inválidos!')

        event_id = self.request.query_params.get('event_id')  # type: ignore
        if not event_id:
            raise ValidationError('event_id é obrigatório!')
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise ValidationError('Evento não encontrado!')
        return event


class PublishPlayersPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'PUT':
            return request.user.has_perm('api.change_event', obj)
        return True


class PublishPlayersResults(BaseView):
    permission_classes = [IsAuthenticated, PublishPlayersPermissions]

    @swagger_auto_schema(
        tags=['player'],
        security=[{'Bearer': []}],
        operation_description='Publica os resultados dos jogadores do evento.',
        operation_summary="""Publica os resultados dos jogadores do evento. Os jogadores poderão ver suas pontuações e os 4 primeiros colocados.""",
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(
            200), **Errors([400]).retrieve_erros()}
    )
    def put(self, request: request.Request, *args, **kwargs) -> response.Response:
        try:
            event = self.get_object()
        except ValidationError as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        event.results_published = True
        event.save()
        return response.Response(status=status.HTTP_200_OK, data='Resultados publicados com sucesso!')

    def get_object(self):
        if 'event_id' not in self.request.query_params:
            raise ValidationError('Dados inválidos!')

        event_id = self.request.query_params.get('event_id')
        if not event_id:
            raise ValidationError('event_id é obrigatório!')
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise ValidationError('Evento não encontrado!')
        return event


class Top3Players(BaseView):
    permission_classes = [IsAuthenticated, PlayersPermission]

    @swagger_auto_schema(
        tags=['player'],
        security=[{'Bearer': []}],
        operation_description='Retorna os 3 jogadores com mais pontos do evento.',
        operation_summary='Retorna os 3 primeiros jogadores do evento.',
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(200, PlayerResultsSerializer), **Errors([400]).retrieve_erros()})
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        try:
            event = self.get_object()
        except ValidationError as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        players = Player.objects.filter(
            event=event).order_by('-total_score')[:3]
        data = PlayerResultsSerializer(players, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    def get_object(self):
        if 'event_id' not in self.request.query_params:
            raise ValidationError('Dados inválidos!')

        event_id = self.request.query_params.get('event_id')
        if not event_id:
            raise ValidationError('event_id é obrigatório!')
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise ValidationError('Evento não encontrado!')
        return event


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
            event = self.get_object()
        except ValidationError as e:
            return handle_400_error(str(e))

        self.check_object_permissions(self.request, event)

        try:
            excel_file = self.get_excel_file()
        except ValidationError as e:
            return handle_400_error(str(e))
        extension = (excel_file.name.split("."))[1]
        df = self.createData(extension=extension, file=excel_file)
        if df is None:
            return handle_400_error('Arquivo inválido!')
        self.create_players(df=df, event=event)
        return response.Response(status=status.HTTP_201_CREATED, data='Jogadores adicionados com sucesso!')

    def create_players(self, df: pd.DataFrame, event: Event) -> None:
        process_data = ['Nome Completo', 'E-mail']
        df_needed = df[process_data]

        for i, line in df_needed.iterrows():
            name = line['Nome Completo']
            email = line['E-mail']
            player, created = Player.objects.get_or_create(
                full_name=name, registration_email=email, event=event)
            if not created:
                player.full_name = name
                player.registration_email = email
                player.event = event
                player.save()

    def createData(self, extension, file) -> Optional[pd.DataFrame]:
        data = None
        if extension == 'csv':
            # Lê os dados do arquivo como uma string
            file_data = file.read().decode('utf-8')
            # Converte a string em um StringIO, que pode ser lido pelo pandas
            csv_data = StringIO(file_data)
            data = pd.read_csv(csv_data, header=0, encoding='utf-8')

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

    def get_object(self):
        if 'event_id' not in self.request.query_params:
            raise ValidationError('Dados inválidos!')

        event_id = self.request.query_params.get('event_id')
        if not event_id:
            raise ValidationError('event_id é obrigatório!')
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise ValidationError('Evento não encontrado!')
        return event


class AddSinglePlayer(BaseView):
    permission_classes = [IsAuthenticated, PlayersPermission]

    @swagger_auto_schema(
        tags=['player'],
        operation_description="""Adiciona um jogador manualmente ao evento.
        Deve ser fornecido o nome completo do jogador como _request body_ e o ID do evento como _manual parameter_. Nome social e email são opcionais.

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
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        full_name = request.data['full_name']
        social_name = request.data['social_name']
        email = request.data['registration_email']
        is_imortal = request.data['is_imortal']
        if not full_name:
            return handle_400_error('Nome completo é obrigatório para criar um jogador!')
        player = Player.objects.create(
            full_name=full_name, social_name=social_name, registration_email=email, event=event, is_imortal=is_imortal, is_present=True)
        data = PlayerSerializer(player).data
        return response.Response(status=status.HTTP_201_CREATED, data=data)
