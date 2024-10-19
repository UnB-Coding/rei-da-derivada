from django.db import transaction
from rest_framework import status, request, response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from .base_views import BaseSumulaView, SUMULA_NOT_FOUND_ERROR_MESSAGE, SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE
from api.models import Staff, SumulaClassificatoria, SumulaImortal, PlayerScore, Player
from ..serializers import PlayerScoreSerializer, SumulaSerializer, SumulaForPlayerSerializer, SumulaImortalSerializer, SumulaClassificatoriaSerializer, SumulaClassificatoriaForPlayerSerializer, SumulaImortalForPlayerSerializer
from rest_framework.permissions import BasePermission
from ..utils import handle_400_error
from ..swagger import Errors, sumula_imortal_api_put_schema, sumula_classicatoria_api_put_schema, sumulas_response_schema, manual_parameter_event_id, sumulas_response_for_player_schema, array_of_sumulas_response_schema
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random
import string
import logging
from django.core.exceptions import ValidationError
SUMULA_IS_CLOSED_ERROR_MESSAGE = "Súmula já encerrada só pode ser editada por um gerente ou adminstrador!"


class HasSumulaPermission(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:

        if request.method == 'POST':
            return request.user.has_perm('api.add_sumula_event', obj)
        elif request.method == 'GET':
            return request.user.has_perm('api.view_sumula_event', obj)
        elif request.method == 'PUT':
            return request.user.has_perm('api.change_sumula_event', obj)
        elif request.method == 'DELETE':
            return request.user.has_perm('api.delete_sumula_event', obj)
        return True


class SumulasView(BaseSumulaView):
    """Lida com os requests relacionados a sumulas."""
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @ swagger_auto_schema(
        tags=['sumula'],
        operation_summary="Retorna todas as sumulas associadas a um evento.",
        operation_description="Retorna todas as sumulas associadas a um evento com seus jogadores e pontuações.",
        security=[{'Bearer': []}],
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response('OK', sumulas_response_schema), **Errors([400]).retrieve_erros()})
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Retorna todas as sumulas associadas a um evento."""
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        sumulas_imortal, sumulas_classificatoria = self.get_sumulas(
            event=event)
        data = SumulaSerializer(
            {'sumulas_classificatoria': sumulas_classificatoria, 'sumulas_imortal': sumulas_imortal}).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    @swagger_auto_schema(
        tags=['sumula'],
        operation_summary="Deleta uma súmula.",
        operation_description="""Deleta uma súmula.
        Apenas um gerente ou administrador do evento pode deletar uma súmula.
        """,
        security=[{'Bearer': []}],
        manual_parameters=manual_parameter_event_id,
        request_body=openapi.Schema(
            title='Sumula',
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID da sumula', example=1),
            },
            required=['id']
        ),
        responses={200: openapi.Response('OK'), **Errors([400]).retrieve_erros()})
    def delete(self, request: request.Request, *args, **kwargs):
        """Deleta uma súmula."""
        if not self.validate_request_data_dict(request.data) or 'id' not in request.data:
            return handle_400_error("Dados inválidos!")
        sumula_id = request.data.get('id')
        if not sumula_id:
            return handle_400_error(SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE)
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        sumula = SumulaImortal.objects.filter(id=sumula_id).first()
        if not sumula:
            sumula = SumulaClassificatoria.objects.filter(id=sumula_id).first()
        if not sumula:
            return handle_400_error(SUMULA_NOT_FOUND_ERROR_MESSAGE)
        sumula.delete()
        return response.Response(status=status.HTTP_200_OK)


class SumulaClassificatoriaView(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @swagger_auto_schema(
        tags=['sumula'],
        operation_summary="Cria uma nova sumula classificatoria.",
        operation_description="Cria uma nova sumula classificatoria e retorna a sumula criada com os jogadores e suas pontuações.",
        security=[{'Bearer': []}],
        manual_parameters=manual_parameter_event_id,
        request_body=openapi.Schema(
            title='Sumula',
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome da sumula'),
                'players': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    title='Players',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador'),
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do jogador'),
                        }
                    ),
                    description='Lista de jogadores',
                ),
                'referees': openapi.Schema(
                    type=openapi.TYPE_ARRAY, title='Staffs',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do Staff')}),
                    description='Lista de objetos Staff'),
            },
            required=['name', 'players'],
        ),
        responses={201: openapi.Response(
            'Created', SumulaClassificatoriaSerializer), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Cria uma nova sumula classificatoria e retorna a sumula criada.

        Permissões necessárias: IsAuthenticated, HasSumulaPermission
        """
        if not self.validate_request_data_dict(request.data) or 'name' not in request.data or not self.validate_players(request.data):
            return handle_400_error("Dados inválidos!")
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        name = request.data['name']
        players = request.data['players']
        sumula = SumulaClassificatoria.objects.create(event=event, name=name)
        try:
            players_score = self.create_players_score(
                players=players, sumula=sumula, event=event)
        except Exception as e:
            return handle_400_error(str(e))
        referees = request.data['referees']
        self.add_referees(sumula=sumula, event=event, referees=referees)
        try:
            sumula.rounds = self.round_robin_tournament(
                len(players_score), players_score)
        except Exception as e:
            return handle_400_error(str(e))
        sumula.save()
        data = SumulaClassificatoriaSerializer(sumula).data
        return response.Response(status=status.HTTP_201_CREATED, data=data)

    @ swagger_auto_schema(
        tags=['sumula'],
        operation_summary="ENCERRA OU EDITA uma sumula classificatoria.",
        operation_description="""Esta rota serve para salvar os dados da sumula e marcar a sumula como **encerrada**.
        As pontuações dos jogadores devem ser enviadas no corpo da requisição e serão atualizadas no banco de dados.
        Devem ser enviados os jogadores **não-classificados** como **IMORTAIS** (is_imortal = True). Já os jogadores **classificados** devem ser enviados como **is_imortal = False.**
        A sumula **não** pode ser mais salva/editada por um monitor comum após encerrada.

**Apenas um gerente ou administrador do evento pode editar uma sumula encerrada.**

        Os campos a serem atualizados são:
        - name
        - description
        - pontuação dos players
        - players que se tornaram imortais
        - define a sumula como encerrada
        """,
        security=[{'Bearer': []}],
        manual_parameters=manual_parameter_event_id,
        request_body=sumula_classicatoria_api_put_schema,
        responses={200: openapi.Response('OK'), **Errors([400]).retrieve_erros()})
    def put(self, request: request.Request, *args, **kwargs):
        """Atualiza uma sumula de Classificatoria
        Obtém o id da sumula a ser atualizada e atualiza os dados associados a ela.
        Obtém uma lista da pontuação dos jogadores e atualiza as pontuações associados a sumula.
        Marca a sumula como encerrada.

        Os campos a serem atualizados são:
        - name
        - description
        - pontuação dos players
        - players que se tornaram imortais
        - define a sumula como encerrada
        """

        required_fields = ['id', 'name', 'description']
        if not self.validate_request_data_dict(request.data) or not all(field in request.data for field in required_fields):
            return handle_400_error("Dados inválidos!")
        if not self.validate_players_score(request.data):
            return handle_400_error("Dados Invalidos!")
        sumula_id = request.data['id']
        if not sumula_id:
            return handle_400_error(SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE)
        sumula = SumulaClassificatoria.objects.filter(id=sumula_id).first()
        if not sumula:
            return handle_400_error(SUMULA_NOT_FOUND_ERROR_MESSAGE)
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        is_admin = request.user.email == event.admin_email
        if not is_admin:
            try:
                staff = self.validate_if_staff_is_sumula_referee(
                    sumula=sumula, event=event)
            except Exception as e:
                return handle_400_error(str(e))
            if not sumula.active and not staff.is_manager:
                return handle_400_error(SUMULA_IS_CLOSED_ERROR_MESSAGE)

        try:
            self.update_sumula(sumula=sumula, event=event)
        except Exception as e:
            return handle_400_error(str(e))
        return response.Response(status=status.HTTP_200_OK)


class SumulaImortalView(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @ swagger_auto_schema(
        tags=['sumula'],
        operation_summary="Cria uma nova sumula imortal.",
        operation_description="""Cria uma nova sumula imortal e retorna a sumula criada com os jogadores e suas pontuações.
        O nome da súmula é criado automaticamente e é composto por "Imortais" + o numero da chave imortal, na ordem em que as súmulas foram criadas.

        Ex: Imortais 01, Imortais 02, Imortais 03, etc.

        No exemplo acima, se a súmula 03 for deletada, a próxima súmula a ser criada será Imortais 03, pois continuará a contagem no maior número existente, que seria 02.
        Já caso a súmula 02 seja deletada e a 03 mantida, a próxima súmula criada será chamada de Imortais 04, pois última súmula tem número 03, não havendo
        possibilidade de reutilizar o número 02.
        """,
        security=[{'Bearer': []}],
        manual_parameters=manual_parameter_event_id,
        request_body=openapi.Schema(
            title='Sumula',
            type=openapi.TYPE_OBJECT,
            properties={
                'players': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    title='Players',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador'),
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do jogador'),
                        }
                    ),
                    description='Lista de jogadores',
                ),
                'referees': openapi.Schema(
                    type=openapi.TYPE_ARRAY, title='Staffs',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do Staff')}),
                    description='Lista de objetos Staff'),
            },
            required=['name', 'players'],
        ),
        responses={201: openapi.Response(
            'Created', SumulaImortalSerializer), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Cria uma nova sumula imortal e retorna a sumula criada.

        Permissões necessárias: IsAuthenticated, HasSumulaPermission
        """
        required_fields = ['players', 'referees']
        if not self.validate_request_data_dict(request.data) or not all(field in request.data for field in required_fields) or not self.validate_players(request.data):
            return handle_400_error("Dados inválidos!")
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)

        players = request.data['players']
        sumula = SumulaImortal.objects.create(
            event=event)
        try:
            players_score = self.create_players_score(
                players=players, sumula=sumula, event=event)
        except Exception as e:
            return handle_400_error(str(e))
        referees = request.data['referees']
        self.add_referees(sumula=sumula, event=event, referees=referees)
        try:
            sumula.rounds = self.round_robin_tournament(
                len(players_score), players_score)
        except Exception as e:
            return handle_400_error(str(e))
        sumula.save()
        data = SumulaImortalSerializer(sumula).data
        return response.Response(status=status.HTTP_201_CREATED, data=data)

    @ swagger_auto_schema(
        tags=['sumula'],
        operation_summary="ENCERRA OU EDITA uma sumula imortal.",
        operation_description="""Esta rota serve para salvar os dados da sumula e marcar a sumula como **encerrada**.
        As pontuações dos jogadores devem ser enviadas no corpo da requisição e serão atualizadas no banco de dados.
        A sumula **não** pode ser mais salva/editada por um monitor comum após encerrada.

**Apenas um gerente ou administrador do evento pode editar uma sumula encerrada.**

        Os campos a serem atualizados são:
        - name
        - description
        - pontuação dos players
        - define a sumula como encerrada
        """,
        security=[{'Bearer': []}],
        manual_parameters=manual_parameter_event_id,
        request_body=sumula_imortal_api_put_schema,
        responses={200: openapi.Response('OK'), **Errors([400]).retrieve_erros()})
    def put(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Atualiza uma sumula Imortal
        Obtém o id da sumula a ser atualizada e atualiza os dados associados a ela.
        Obtém uma lista da pontuação dos jogadores e atualiza as pontuações associados a sumula.
        Marca a sumula como encerrada.
        """
        required_fields = ['id', 'name', 'description']
        if not self.validate_request_data_dict(request.data) or not all(field in request.data for field in required_fields):
            return handle_400_error("Dados inválidos!")
        sumula_id = request.data['id']
        if not sumula_id:
            return handle_400_error(SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE)
        sumula = SumulaImortal.objects.filter(id=sumula_id).first()
        if not sumula:
            return handle_400_error(SUMULA_NOT_FOUND_ERROR_MESSAGE)
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        is_admin = request.user.email == event.admin_email
        if not is_admin:
            try:
                staff = self.validate_if_staff_is_sumula_referee(
                    sumula=sumula, event=event)
            except Exception as e:
                return handle_400_error(str(e))
            if not sumula.active and not staff.is_manager:
                return handle_400_error(SUMULA_IS_CLOSED_ERROR_MESSAGE)

        try:
            self.update_sumula(sumula=sumula, event=event)
        except Exception as e:
            return handle_400_error(str(e))
        return response.Response(status=status.HTTP_200_OK)


class ActiveSumulaView(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @ swagger_auto_schema(
        tags=['sumula'],
        operation_summary="Retorna todas as sumulas ativas associadas a um evento.",
        operation_description="Retorna todas as sumulas ativas associadas a um evento, com seus jogadores e pontuações.",
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(
            'OK', sumulas_response_schema), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request):
        """Retorna todas as sumulas ativas."""
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        sumula_imortal, sumula_classificatoria = self.get_sumulas(
            event=event, active=True)
        data = SumulaSerializer(
            {'sumulas_classificatoria': sumula_classificatoria, 'sumulas_imortal': sumula_imortal}).data
        return response.Response(status=status.HTTP_200_OK, data=data)


class FinishedSumulaView(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @ swagger_auto_schema(
        tags=['sumula'],
        operation_summary="Retorna todas as sumulas encerradas associadas a um evento.",
        operation_description="Retorna todas as sumulas encerradas associadas a um evento, com seus jogadores e pontuações.",
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(
            'OK', sumulas_response_schema), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request):
        """Retorna todas as sumulas encerradas."""
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        sumula_imortal, sumula_classificatoria = self.get_sumulas(
            event=event, active=False)
        data = SumulaSerializer(
            {'sumulas_classificatoria': sumula_classificatoria, 'sumulas_imortal': sumula_imortal}).data
        return response.Response(status=status.HTTP_200_OK, data=data)


class GetSumulaForPlayerPermission(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if request.method == 'GET':
            return request.user.has_perm('api.view_event', obj)
        return False


class GetSumulaForPlayer(BaseSumulaView):
    permission_classes = [IsAuthenticated, GetSumulaForPlayerPermission]

    @ swagger_auto_schema(
        tags=['sumula'],
        operation_summary="Retorna as sumulas ativas para um jogador.",
        operation_description="""
        Retorna todas as sumulas ativas para o jogador. São omitidos pontuações da sumula.""",
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(
            'OK', sumulas_response_for_player_schema), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Retorna todas as sumulas ativas associadas a um jogador."""
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)

        player = Player.objects.filter(user=request.user, event=event).first()
        if not player:
            return handle_400_error("Jogador não encontrado!")

        if player.is_imortal:
            player_scores = PlayerScore.objects.filter(
                player=player, sumula_imortal__active=True)
            if not player_scores:
                return handle_400_error("Jogador não possui nenhuma sumula associada!")
            sumulas = [
                player_score.sumula_imortal for player_score in player_scores]
            data = SumulaImortalForPlayerSerializer(
                sumulas, many=True).data
        else:
            player_scores = PlayerScore.objects.filter(
                player=player, sumula_classificatoria__active=True)
            if not player_scores:
                return handle_400_error("Jogador não possui nenhuma sumula associada!")
            sumulas = [
                player_score.sumula_classificatoria for player_score in player_scores]
            data = SumulaClassificatoriaForPlayerSerializer(
                sumulas, many=True).data

        return response.Response(status=status.HTTP_200_OK, data=data)


class AddRefereeToSumulaView(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @swagger_auto_schema(
        tags=['sumula'],
        operation_description="""
        Adiciona um árbitro a uma súmula que já existe.
        Caso uma súmula seja criada sem nenhum árbitro, é possível que um usuário monitor se auto adicione como árbitro ao selecionar a sumula desejada.
        Apenas o usuário que fez a requisição será adicionado como árbitro da súmula.
        Esta rota verifica se o usuário em questão tem as permissões necessárias para ser um árbitro no evento e se possui um objeto staff associado a ele.

            É necessário fornecer o id da súmula e indicar se a súmula é imortal ou classificatória no corpo da requisição.
        """,
        operation_summary="Adiciona um árbitro a uma súmula.",
        request_body=openapi.Schema(
            title='Sumula',
            type=openapi.TYPE_OBJECT,
            properties={
                'sumula_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Id da sumula imortal'),
                'is_imortal': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indica se a sumula é imortal ou classificatória', example=True)
            },
            required=['sumula_id', 'is_imortal'],
        ),
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response('OK'), **Errors([400]).retrieve_erros()})
    def put(self, request: request.Request, *args, **kwargs):
        if not self.validate_request_data_dict(request.data) or 'sumula_id' not in request.data or 'is_imortal' not in request.data:
            return handle_400_error("Dados inválidos!")
        sumula_id = request.data.get('sumula_id')
        if not sumula_id:
            return handle_400_error(SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE)
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        if event.admin_email == request.user.email:
            return response.Response(status=status.HTTP_200_OK)

        staff = Staff.objects.filter(
            user=request.user, event=event).first()
        if not staff:
            return handle_400_error("Usuário não é um monitor do evento!")

        is_imortal = request.data.get('is_imortal')
        if is_imortal:
            sumula = SumulaImortal.objects.filter(id=sumula_id).first()
        else:
            sumula = SumulaClassificatoria.objects.filter(id=sumula_id).first()
        if not sumula:
            return handle_400_error(SUMULA_NOT_FOUND_ERROR_MESSAGE)

        if sumula.referee.all().count() > 0 and staff not in sumula.referee.all():
            return handle_400_error("Súmula já possui um ou mais árbitros!")
        elif sumula.referee.all().count() == 0:
            sumula.referee.add(staff)
        return response.Response(status=status.HTTP_200_OK)


class GenerateSumulas(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @swagger_auto_schema(
        tags=['sumula'],
        operation_summary="Gera sumulas classificatorias para iniciar um evento.",
        operation_description="""Gera sumulas classificatorias para iniciar um evento.
        Uma sumula possui no maximo 8 e no mínimo 6 jogadores.
        Apenas um gerente ou administrador do evento pode gerar sumulas.

        **Essa ação só pode ser realizada uma vez durante o evento.**
        """,
        security=[{'Bearer': []}],
        manual_parameters=manual_parameter_event_id,
        responses={201: openapi.Response(
            'Created', array_of_sumulas_response_schema), **Errors([400]).retrieve_erros()})
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        if event.is_sumulas_generated:
            return handle_400_error(
                "As sumulas iniciais já foram geradas para este evento!")
        try:
            sumulas = self.generate_sumulas(
                event=event)
        except Exception as e:
            return handle_400_error(str(e))
        event.is_sumulas_generated = True
        event.save()
        return response.Response(status=status.HTTP_201_CREATED, data="Sumulas geradas com sucesso!")

    def generate_sumulas(self, event) -> list[SumulaClassificatoria] | Exception:
        logger = logging.getLogger(__name__)
        """Gera sumulas classificatorias para iniciar um evento.
        Uma sumula possui no maximo 8 e no mínimo 6 jogadores.
        """
        MIN_PLAYERS = 6  # A DECIDIR
        MAX_PLAYERS = 8
        letters = string.ascii_uppercase  # Alfabeto para nomear as chaves
        letters_count = 0

        try:
            with transaction.atomic():
                players = Player.objects.filter(
                    event=event, is_present=True, is_imortal=False).select_for_update()
                if players.count() < MIN_PLAYERS:
                    logger.error(f"O evento precisa de pelo menos {MIN_PLAYERS} jogadores presentes para iniciar.")
                    raise ValidationError(f"O evento precisa de pelo menos {MIN_PLAYERS} jogadores presentes para iniciar.")

                players = list(players)
                random.shuffle(players)
                N = len(players)
                resto = N % MAX_PLAYERS
                n_sumulas = N // MAX_PLAYERS
                sumulas: list[SumulaClassificatoria] = []

                if resto > 0:
                    n_sumulas += 1

                for i in range(n_sumulas):
                    if letters_count % 26 == 0:
                        letters_count = 0
                    if i < 26:
                        sumula = SumulaClassificatoria.objects.create(
                            event=event, name=f"Chave {letters[letters_count]}")
                    else:
                        name = f"{letters[letters_count]}" * (i // 26 + 1)
                        sumula = SumulaClassificatoria.objects.create(
                            event=event, name=f"Chave {name}")
                    letters_count += 1
                    sumulas.append(sumula)
                    players_to_add = players[i *
                                             MAX_PLAYERS:(i + 1) * MAX_PLAYERS]
                    for j in range(len(players_to_add)):
                        player = players_to_add[j]
                        PlayerScore.objects.create(
                            event=event, player=player, sumula_classificatoria=sumulas[i])

                if resto > 0 and resto < MIN_PLAYERS:
                    index_of_complete_sumulas = n_sumulas - 2
                    last_sumula = sumulas[n_sumulas - 1]
                    while last_sumula.scores.count() < MIN_PLAYERS:
                        scores = sumulas[index_of_complete_sumulas].scores.all()
                        for i in range(2):
                            player = scores[i].player
                            scores[i].delete()
                            PlayerScore.objects.create(
                                event=event, player=player, sumula_classificatoria=last_sumula)
                            last_sumula.refresh_from_db(fields=['scores'])
                            if last_sumula.scores.count() == MIN_PLAYERS:
                                break
                        index_of_complete_sumulas -= 1

                for sumula in sumulas:
                    players_list = [player for player in sumula.scores.all()]
                    sumula.rounds = self.round_robin_tournament(
                        n=len(players_list), players_score=players_list)
                    sumula.save()

            logger.info(
                f"{len(sumulas)} sumulas classificatorias geradas para o evento {event.id}")
        except ValidationError as e:
            logger.error(f"Erro de validação ao gerar sumulas: {e}")
            return handle_400_error(f"Erro de validação ao gerar sumulas: {e}")
        except Exception as e:
            logger.error(f"Erro ao gerar sumulas: {e}")
            return handle_400_error(f"Erro ao gerar sumulas: {e}")

        return sumulas


class RemovePlayersFromSumula(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @ swagger_auto_schema(
        tags=['sumula'],
        operation_summary="Remove jogadores de uma súmula.",
        operation_description="""Esta rota serve para salvar os dados da sumula e marcar a sumula como **encerrada**..
        Apenas um gerente ou administrador do evento pode remover jogadores de uma sumula.
        """,
        security=[{'Bearer': []}],
        manual_parameters=manual_parameter_event_id,
        request_body=openapi.Schema(
            title='Sumula',
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID da sumula', example=1),
                'players_to_delete': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        title='PlayerScore',
                        type=openapi.TYPE_OBJECT,
                        description='Objetos de pontuacao dos jogadores que devem ser removidos da sumula',
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do objeto de pontuacao do jogador', example=1),
                            'player': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                title='Player',
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador', example=1),
                                    'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome completo do jogador', example='João Silva Jacinto '),
                                    'social_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome social do jogador', example='João Silva'),
                                },
                                required=['id']
                            ),
                        },
                        required=['id', 'player']
                    )
                ),
            },
            required=['id', 'name', 'referee', 'players_score']
        ),
        responses={200: openapi.Response('OK'), **Errors([400]).retrieve_erros()})
    def put(self, request: request.Request, *args, **kwargs):
        """Remove jogadores de uma sumula."""
        a = 1
