from typing import Optional
from requests import Response
from rest_framework import status, request, response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.models import Token, Event, Sumula, PlayerScore, PlayerTotalScore
from users.models import User
from ..serializers import SumulaSerializer, PlayerScoreSerializerForSumula
from rest_framework.permissions import BasePermission
from ..utils import handle_400_error
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..swagger import Errors


class HasSumulaPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.has_perm('api.add_sumula')
        elif request.method == 'GET':
            return request.user.has_perm('api.view_sumula')
        elif request.method == 'PUT':
            return request.user.has_perm('api.change_sumula')
        return True


class SumulaView(APIView):
    """Lida com os requests relacionados a sumulas."""
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    def create_players_score(self, players: list, sumula: Sumula, event: Event) -> None:
        """Cria uma lista de PlayerScore associados a uma sumula."""
        for player in players:
            user = User.objects.filter(id=player['user_id']).first()
            if not user:
                continue
            player_score = PlayerScore.objects.create(
                user=user, sumula=sumula, points=0, event=event)
            player_score.save()

    @swagger_auto_schema(
        operation_summary="Cria uma nova sumula.",
        operation_id='create_sumula',
        operation_description="Cria uma nova sumula e retorna a sumula criada com os jogadores e suas pontuações.",
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.", type=openapi.TYPE_INTEGER, required=True)],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'players': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID do usuário"),
                        },
                        required=['user_id'],
                        description="Objeto representando um jogador"
                    ),
                    description="Lista de IDs de jogadores"
                )
            },
            required=['players'],
            description="Objetos necessário para criar uma nova sumula"
        ),
        responses={201: openapi.Response(
            'Created', SumulaSerializer), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs):
        """Cria uma nova sumula e retorna a sumula criada.

        Permissões necessárias: IsAuthenticated, HasSumulaPermission
        """
        if not request.data or not isinstance(request.data, dict) or 'players' not in request.data.keys():
            return handle_400_error("Dados inválidos!")

        event_id = request.query_params.get('event_id')
        event = Event.objects.filter(id=event_id).first()

        if not event:
            return handle_400_error("Evento não encontrado!")
        players = request.data['players']
        for player in players:
            if 'user_id' not in player:
                return handle_400_error("Dados inválidos!")
        sumula = Sumula.objects.create(event=event)
        self.create_players_score(players=players, sumula=sumula, event=event)
        data = SumulaSerializer(sumula).data
        return response.Response(status=status.HTTP_201_CREATED, data=data)

    @swagger_auto_schema(
        operation_summary="Retorna todas as sumulas associadas a um evento.",
        operation_id='get_sumulas',
        operation_description="Retorna todas as sumulas associadas a um evento com seus jogadores e pontuações.",
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.", type=openapi.TYPE_INTEGER, required=True)],
        responses={200: openapi.Response('OK', SumulaSerializer), **Errors([400]).retrieve_erros()})
    def get(self, request: request.Request, *args, **kwargs):
        """Retorna todas as sumulas associadas a um evento."""
        event_id = request.query_params.get('event_id')
        if not event_id:
            return handle_400_error("Dados inválidos!")

        event = Event.objects.filter(id=event_id).first()
        sumulas = Sumula.objects.filter(event=event)

        data = SumulaSerializer(sumulas, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    @swagger_auto_schema(operation_id='update_sumula',
                         operation_summary="Atualiza uma sumula.",
                         operation_description="""Atualiza os dados associados a uma sumula criada.
                         """,
                         security=[{'Bearer': []}],
                         request_body=SumulaSerializer,
                         responses={200: openapi.Response('OK'), **Errors([400]).retrieve_erros()})
    def put(self, request: request.Request, *args, **kwargs):
        """Atualiza uma sumula."""
        if not request.data or not isinstance(request.data, dict) or 'sumula_id' not in request.data.keys():
            return handle_400_error("Dados inválidos!")
        # Necessario mudar isso para request.get('sumula_id') para pegar o id da query
        sumula_id = request.query_params.get('sumula_id')
        sumula = Sumula.objects.filter(id=sumula_id).first()
        if not sumula:
            return handle_400_error("Sumula não encontrada!")
        # sumula.active = False
        sumula.save()
        return response.Response(status=status.HTTP_200_OK)


class ActiveSumulaView(APIView):
    @swagger_auto_schema(operation_id='get_active_sumulas',
                         operation_summary="Retorna todas as sumulas ativas associadas a um evento.",
                         operation_description="Retorna todas as sumulas ativas associadas a um evento, com seus jogadores e pontuações.",
                         manual_parameters=[openapi.Parameter(
                             'event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.", type=openapi.TYPE_INTEGER, required=True)],
                         responses={200: openapi.Response(
                             'OK', SumulaSerializer), **Errors([400]).retrieve_erros()}
                         )
    def get(self, request: request.Request):
        """Retorna todas as sumulas ativas."""
        event_id = request.query_params.get('event_id')
        if not event_id:
            return handle_400_error("Dados inválidos!")

        event = Event.objects.filter(id=event_id).first()
        sumulas = Sumula.objects.filter(event=event, active=True)
        data = SumulaSerializer(sumulas, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)
