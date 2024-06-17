from django.forms import ValidationError
from django.contrib.auth.models import Group
from django.db.models import Q
from rest_framework import status, request, response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission
from base_views import BaseSumulaView
from api.models import Event, SumulaClassificatoria, SumulaImortal, PlayerScore, Player
from users.models import User
from ..serializers import SumulaSerializer, SumulaForPlayerSerializer, SumulaImortalSerializer, SumulaClassificatoriaSerializer, ActiveSumulaSerializer, FinishedSumulaSerializer
from rest_framework.permissions import BasePermission
from ..utils import handle_400_error
from ..swagger import Errors, sumula_imortal_api_put_schema, sumula_classicatoria_api_put_schema
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
EVENT_NOT_FOUND_ERROR_MESSAGE = "Evento não encontrado!"
EVENT_ID_NOT_PROVIDED_ERROR_MESSAGE = "Id do evento não fornecido!"
SUMULA_NOT_FOUND_ERROR_MESSAGE = "Sumula não encontrada!"
SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE = "Id da sumula não fornecido!"
SUMULA_NOT_FOUND_ERROR_MESSAGE = "Sumula não encontrada!"


class HasSumulaPermission(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if Group.objects.get(name='app_admin') in request.user.groups.all():
            return True

        if request.method == 'POST':
            return request.user.has_perm('api.add_sumula_event', obj)
        elif request.method == 'GET':
            return request.user.has_perm('api.view_sumula_event', obj)
        elif request.method == 'PUT':
            return request.user.has_perm('api.change_sumula_event', obj)
        elif request.method == 'DELETE':
            return request.user.has_perm('api.delete_sumula_event', obj)
        return True


class SumulaView(BaseSumulaView):
    """Lida com os requests relacionados a sumulas."""
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @ swagger_auto_schema(
        operation_summary="Retorna todas as sumulas associadas a um evento.",
        operation_description="Retorna todas as sumulas associadas a um evento com seus jogadores e pontuações.",
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, description="Id do evento associado às sumulas.", type=openapi.TYPE_INTEGER, required=True)],
        responses={200: openapi.Response('OK', SumulaSerializer), **Errors([400]).retrieve_erros()})
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Retorna todas as sumulas associadas a um evento."""
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        data = SumulaSerializer(event).data
        return response.Response(status=status.HTTP_200_OK, data=data)


class SumulaClassificatoriaView(SumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @swagger_auto_schema(
        operation_summary="Cria uma nova sumula classificatoria.",
        operation_description="Cria uma nova sumula classificatoria e retorna a sumula criada com os jogadores e suas pontuações.",
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.", type=openapi.TYPE_INTEGER, required=True)],
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
                        }
                    ),
                    description='Lista de jogadores',
                ),
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
        if not self.validate_request_data(request.data):
            return handle_400_error("Dados inválidos!")
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))

        if not self.validate_players(request.data):
            return handle_400_error("Dados de players inválidos!")

        self.check_object_permissions(self.request, event)

        players = request.data['players']
        sumula = SumulaClassificatoria.objects.create(event=event)
        self.create_players_score(players=players, sumula=sumula, event=event)
        data = SumulaClassificatoriaSerializer(sumula).data
        return response.Response(status=status.HTTP_201_CREATED, data=data)

    @ swagger_auto_schema(
        operation_summary="Atualiza uma sumula.",
        operation_description="""Atualiza os dados associados a uma sumula criada.
                         """,
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter('event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.",
                                             type=openapi.TYPE_INTEGER, required=True)],
        request_body=sumula_imortal_api_put_schema,
        responses={200: openapi.Response('OK'), **Errors([400]).retrieve_erros()})
    def put(self, request: request.Request, *args, **kwargs):
        """Atualiza uma sumula de Classificatoria"""
        a = 1


class SumulaImortalView(SumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @swagger_auto_schema(
        operation_summary="Cria uma nova sumula imortal.",
        operation_description="Cria uma nova sumula imortal e retorna a sumula criada com os jogadores e suas pontuações.",
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.", type=openapi.TYPE_INTEGER, required=True)],
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
                        }
                    ),
                    description='Lista de jogadores',
                ),
            },
            required=['name', 'players'],
        ),
        responses={201: openapi.Response(
            'Created', SumulaClassificatoriaSerializer), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Cria uma nova sumula imortal e retorna a sumula criada.

        Permissões necessárias: IsAuthenticated, HasSumulaPermission
        """
        if not self.validate_request_data(request.data):
            return handle_400_error("Dados inválidos!")
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        if not self.validate_players(request.data):
            return handle_400_error("Dados de players inválidos!")

        self.check_object_permissions(self.request, event)

        players = request.data['players']
        sumula = SumulaImortal.objects.create(event=event)
        self.create_players_score(players=players, sumula=sumula, event=event)
        data = SumulaImortalSerializer(sumula).data
        return response.Response(status=status.HTTP_201_CREATED, data=data)

    @ swagger_auto_schema(
        operation_summary="Atualiza uma sumula Imortal.",
        operation_description="""Atualiza uma sumula
        Obtém o id da sumula a ser atualizada e atualiza os dados associados a ela.
        Obtém uma lista da pontuação dos jogadores e atualiza as pontuações associados a sumula.
        Marca a sumula como encerrada """,
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter('event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.",
                                             type=openapi.TYPE_INTEGER, required=True)],
        request_body=sumula_imortal_api_put_schema,
        responses={200: openapi.Response('OK'), **Errors([400]).retrieve_erros()})
    def put(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Atualiza uma sumula
        Obtém o id da sumula a ser atualizada e atualiza os dados associados a ela.
        Obtém uma lista da pontuação dos jogadores e atualiza as pontuações associados a sumula.
        Marca a sumula como encerrada.
        """

        if not request.data or not isinstance(request.data, list) or 'id' not in request.data[0]:
            return handle_400_error("Dados inválidos!")

        sumula_id = request.data[0]['id']
        if not sumula_id:
            return handle_400_error(SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE)
        sumula = SumulaImortal.objects.filter(id=sumula_id).first()
        if not sumula:
            return handle_400_error(SUMULA_NOT_FOUND_ERROR_MESSAGE)
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))

        # Verifica se o usuário tem permissão para acessar o evento
        self.check_object_permissions(request, event)
        if 'name' not in request.data[0] or 'description' not in request.data[0] or 'referee' not in request.data[0]:
            return handle_400_error("Dados inválidos!")
        sumula.name = request.data[0]['name']
        sumula.description = request.data[0]['description']
        # referees = request.data[0]['referee']
        # self.add_referee(sumula, referees) necessario refatorar com outra rota apenas para atribuir referee.

        players_score = request.data[0]['players_score']

        if not self.update_player_score(players_score):
            return handle_400_error("Dados de pontuação inválidos!")

        sumula.active = False
        sumula.save()
        return response.Response(status=status.HTTP_200_OK)


class ActiveSumulaView(APIView, BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @ swagger_auto_schema(
        operation_summary="Retorna todas as sumulas ativas associadas a um evento.",
        operation_description="Retorna todas as sumulas ativas associadas a um evento, com seus jogadores e pontuações.",
        manual_parameters=[openapi.Parameter(
                              'event_id', openapi.IN_QUERY, description="Id do evento associado às sumulas.", type=openapi.TYPE_INTEGER, required=True)],
        responses={200: openapi.Response(
            'OK', SumulaSerializer), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request):
        """Retorna todas as sumulas ativas."""
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        data = ActiveSumulaSerializer(event, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)


class FinishedSumulaView(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @ swagger_auto_schema(
        operation_summary="Retorna todas as sumulas encerradas associadas a um evento.",
        operation_description="Retorna todas as sumulas encerradas associadas a um evento, com seus jogadores e pontuações.",
        manual_parameters=[openapi.Parameter(
                              'event_id', openapi.IN_QUERY, description="Id do evento associado às sumulas.", type=openapi.TYPE_INTEGER, required=True)],
        responses={200: openapi.Response(
            'OK', SumulaSerializer), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request):
        """Retorna todas as sumulas encerradas."""
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        data = FinishedSumulaSerializer(event, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)


class GetSumulaForPlayerPermission(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if Group.objects.get(name='app_admin') in request.user.groups.all():
            return True
        if request.method == 'GET':
            return request.user.has_perm('api.view_event', obj)
        return False


class GetSumulaForPlayer(BaseSumulaView):
    permission_classes = [IsAuthenticated, GetSumulaForPlayerPermission]

    @ swagger_auto_schema(
        operation_summary="Retorna as sumulas ativas para um jogador.",
        operation_description="""
        Retorna todas as sumulas ativas para o jogador. São omitidos pontuações da sumula.""",
        manual_parameters=[openapi.Parameter(
                              'event_id', openapi.IN_QUERY, description="Id do evento associado às sumulas.", type=openapi.TYPE_INTEGER, required=True)],
        responses={200: openapi.Response(
            'OK', SumulaForPlayerSerializer), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Retorna todas as sumulas ativas associadas a um jogador."""
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)

        player = Player.objects.filter(user=request.user, event=event).first()
        if player.is_imortal:
            player_scores = PlayerScore.objects.filter(
                player=player, sumula_imortal__active=True)
        else:
            player_scores = PlayerScore.objects.filter(
                player=player, sumula_classificatoria__active=True)
        if not player_scores:
            return handle_400_error("Jogador não possui nenhuma sumula associada!")
        sumulas = [player_score.sumula_imortal for player_score in player_scores] if player.is_imortal else [
            player_score.sumula_classificatoria for player_score in player_scores]
        data = SumulaForPlayerSerializer(sumulas, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)
