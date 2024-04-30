from typing import Optional
from requests import Response
from rest_framework import status, request, response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.models import Token, Event, Sumula, PlayerScore, PlayerTotalScore
from users.models import User
from ..serializers import TokenSerializer, EventSerializer, PlayerTotalScoreSerializer, PlayerScoreSerializer, SumulaSerializer, UserSerializer
from rest_framework.permissions import BasePermission
from ..utils import handle_400_error


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

    def post(self, request: request.Request):
        """Cria uma nova sumula e retorna a sumula criada."""
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

    def get(self, request: request.Request):
        """Retorna todas as sumulas."""
        event_id = request.query_params.get('event_id')
        if not event_id:
            return handle_400_error("Dados inválidos!")

        event = Event.objects.filter(id=event_id).first()
        sumulas = Sumula.objects.filter(event=event)

        data = SumulaSerializer(sumulas, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    def get_active(self, request: request.Request):
        """Retorna todas as sumulas ativas."""
        event_id = request.query_params.get('event_id')
        if not event_id:
            return handle_400_error("Dados inválidos!")

        event = Event.objects.filter(id=event_id).first()
        sumulas = Sumula.objects.filter(event=event, active=True)
        data = SumulaSerializer(sumulas, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    def put(self, request: request.Request):
        """Atualiza uma sumula."""
        if not request.data or not isinstance(request.data, dict) or 'sumula_id' not in request.data.keys():
            return handle_400_error("Dados inválidos!")

        sumula_id = request.query_params.get('sumula_id')
        sumula = Sumula.objects.filter(id=sumula_id).first()
        if not sumula:
            return handle_400_error("Sumula não encontrada!")
        sumula.active = False
        sumula.save()
        return response.Response(status=status.HTTP_200_OK)
