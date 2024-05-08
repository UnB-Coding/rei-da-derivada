from typing import Optional
from rest_framework import status, request, response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.models import Event, Sumula, PlayerScore, Player
from users.models import User
from ..serializers import PlayerSerializer, PlayerScoreSerializer, SumulaSerializer, UserSerializer
from rest_framework.permissions import BasePermission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ..utils import handle_400_error
from ..swagger import Errors


class PlayersPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.has_perm('api.view_player')
        if request.method == 'POST':
            return request.user.has_perm('api.add_player')
        if request.method == 'PUT':
            return request.user.has_perm('api.change_player')
        if request.method == 'DELETE':
            return request.user.has_perm('api.delete_player')

        return True


class PlayersView(APIView):

    permission_classes = [IsAuthenticated, PlayersPermission]

    @ swagger_auto_schema(security=[{'Bearer': []}],
                          operation_description='Retorna todos os jogadores de um evento.',
                          operation_summary='Retorna todos os jogadores de um evento.',
                          operation_id='get_all_players',
                          manual_parameters=[openapi.Parameter(
                              'event_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Id do evento')],
                          responses={200: openapi.Response(200, PlayerSerializer), **Errors([400]).retrieve_erros()})
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        event_id = request.query_params.get('event_id')
        if not event_id:
            return handle_400_error('event_id é obrigatório!')
        event = Event.objects.filter(id=event_id).first()
        if not event:
            return handle_400_error('Evento não encontrado!')

        players = Player.objects.filter(event=event)
        if not players:
            return response.Response(status=status.HTTP_200_OK, data=['Nenhum jogador encontrado!'])
        players_list = []
        for player in players:
            players_list.append(player)

        data = PlayerSerializer(players_list, many=True).data

        return response.Response(status=status.HTTP_200_OK, data=data)


class GetCurrentPlayer(APIView):
    permission_classes = [IsAuthenticated, PlayersPermission]

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        operation_summary='Retorna as informações do jogador atual do usuário logado.',
        operation_description='Retorna apenas o jogador do evento atual do usuário logado.',
        operation_id='get_current_player',
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Id do evento')],
        responses={200: openapi.Response(200, PlayerSerializer), **Errors([400]).retrieve_erros()})
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        event_id = request.query_params.get('event_id')
        if not event_id:
            return handle_400_error('event_id é obrigatório!')
        event = Event.objects.filter(id=event_id).first()
        if not event:
            return handle_400_error('Evento não encontrado!')

        player = Player.objects.filter(event=event, user=request.user).first()
        if not player:
            return handle_400_error('Jogador não encontrado!')

        data = PlayerSerializer(player).data

        return response.Response(status=status.HTTP_200_OK, data=data)
