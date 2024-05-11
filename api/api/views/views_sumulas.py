from typing import Optional
from django.forms import ValidationError
from requests import Response
from django.contrib.auth.models import Group
from rest_framework import status, request, response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from api.models import Event, Sumula, PlayerScore, Player
from users.models import User
from ..serializers import PlayerSerializer, PlayerSerializerForSumula, SumulaSerialiazerForPost, SumulaSerializer
from rest_framework.permissions import BasePermission
from ..utils import handle_400_error
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..swagger import Errors
from ..permissions import assign_permissions
from rest_framework.exceptions import NotFound
from guardian.shortcuts import get_perms
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


class SumulaView(APIView):
    """Lida com os requests relacionados a sumulas."""
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @swagger_auto_schema(
        operation_summary="Cria uma nova sumula.",
        operation_id='create_sumula',
        operation_description="Cria uma nova sumula e retorna a sumula criada com os jogadores e suas pontuações.",
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.", type=openapi.TYPE_INTEGER, required=True)],
        request_body=openapi.Schema(
            title='Sumula',
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome da sumula'),
                'event': openapi.Schema(type=openapi.TYPE_OBJECT, properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do evento')}),
                'players': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador'),
                            'total_score': openapi.Schema(type=openapi.TYPE_INTEGER, description='Pontuação total do jogador'),
                            'user': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do usuário'),
                                        'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Primeiro nome'),
                                        'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Último nome'),
                                    }
                                ),
                                description='Lista de usuários',
                            ),
                        }
                    ),
                    description='Lista de jogadores',
                ),
            },
            required=['name', 'event', 'players'],
        ),
        responses={201: openapi.Response(
            'Created', SumulaSerializer), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Cria uma nova sumula e retorna a sumula criada.

        Permissões necessárias: IsAuthenticated, HasSumulaPermission
        """
        if not request.data or not isinstance(request.data, dict):
            return handle_400_error("Dados inválidos!")
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        if 'players' not in request.data:
            return handle_400_error("Players não fornecidos!")
        try:
            self.check_object_permissions(self.request, event)
        except PermissionDenied as e:
            return response.Response(status=status.HTTP_403_FORBIDDEN, data=str(e))

        players = request.data['players']
        for player in players:
            if 'id' not in player:
                return handle_400_error("Id do jogador não fornecido!")

        sumula = Sumula.objects.create(event=event)
        self.create_players_score(players=players, sumula=sumula, event=event)
        data = SumulaSerializer(sumula).data
        return response.Response(status=status.HTTP_201_CREATED, data=data)

    @ swagger_auto_schema(
        operation_summary="Retorna todas as sumulas associadas a um evento.",
        operation_id='get_sumulas',
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
        sumulas = Sumula.objects.filter(event=event)
        data = SumulaSerializer(sumulas, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    @ swagger_auto_schema(operation_id='update_sumula',
                          operation_summary="Atualiza uma sumula.",
                          operation_description="""Atualiza os dados associados a uma sumula criada.
                         """,
                          security=[{'Bearer': []}],
                          request_body=SumulaSerializer,
                          responses={200: openapi.Response('OK'), **Errors([400]).retrieve_erros()})
    def put(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Atualiza uma sumula
        Obtém o id da sumula a ser atualizada e atualiza os dados associados a ela.
        Obtém uma lista de jogadores e suas pontuações e atualiza as pontuações dos jogadores associados a sumula.
        Marca a sumula como encerrada.
        """

        if not request.data or not isinstance(request.data, list) or 'id' not in request.data[0]:
            return handle_400_error("Dados inválidos!")

        sumula_id = request.data[0]['id']
        if not sumula_id:
            return handle_400_error(SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE)
        sumula = Sumula.objects.filter(id=sumula_id).first()
        if not sumula:
            return handle_400_error(SUMULA_NOT_FOUND_ERROR_MESSAGE)
        event = sumula.event
        # Verifica se o usuário tem permissão para acessar o evento
        self.check_object_permissions(request, event)

        sumula.name = request.data[0]['name']
        referees = request.data[0]['referee']
        self.add_referee(sumula, referees)

        players_score = request.data[0]['players_score']

        if not self.update_player_score(players_score):
            return handle_400_error("Dados de pontuação inválidos!")

        sumula.active = False
        sumula.save()
        return response.Response(status=status.HTTP_200_OK)

    def create_players_score(self, players: list, sumula: Sumula, event: Event) -> None:
        """Cria uma lista de PlayerScore associados a uma sumula."""
        for player in players:
            player_id = player.get('id')
            if player_id is None:
                continue
            player_obj = Player.objects.filter(id=player_id).first()
            if not player_obj:
                continue
            PlayerScore.objects.create(
                player=player_obj, sumula=sumula, event=event)

    def add_referee(self, sumula: Sumula, referees: list) -> None:
        """Adiciona um árbitro a uma sumula."""
        for referee in referees:
            user = User.objects.filter(id=referee['id']).first()
            if not user:
                continue
            sumula.referee.add(user)

    def update_player_score(self, players_score: list[dict]) -> bool:
        """Atualiza a pontuação de um jogador."""
        for player_score in players_score:
            player_score_id = player_score.get('id')
            if player_score_id is None:
                return False
            player_score_obj = PlayerScore.objects.filter(
                id=player_score_id).first()
            if not player_score_obj:
                return False
            player_score_obj.points = player_score['points']
            player_score_obj.save()
        return True

    def get_object(self) -> Event:
        """ Verifica se o evento existe e se o usuário tem permissão para acessá-lo.
        Retorna o evento associado ao id fornecido.
        """
        event_id = None
        # Verifica se o event_id está nos dados da requisição
        if 'event' in self.request.data and isinstance(self.request.data['event'], dict) and 'id' in self.request.data['event']:
            event_id = self.request.data['event'].get('id')

        # Se não estiver nos dados da requisição, verifica se está nos parâmetros da consulta
        if not event_id:

            event_id = self.request.query_params.get('event_id')

        if not event_id:
            raise ValidationError(EVENT_ID_NOT_PROVIDED_ERROR_MESSAGE)

        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise NotFound(EVENT_NOT_FOUND_ERROR_MESSAGE)
        return event


class ActiveSumulaView(APIView):
    @ swagger_auto_schema(operation_id='get_active_sumulas',
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
        sumulas = Sumula.objects.filter(event=event, active=True)
        data = SumulaSerializer(sumulas, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    def get_object(self) -> Event:
        """ Verifica se o evento existe e se o usuário tem permissão para acessá-lo.
        Retorna o evento associado ao id fornecido.
        """
        event_id = self.request.query_params.get('event_id')
        if not event_id:
            raise ValidationError(EVENT_ID_NOT_PROVIDED_ERROR_MESSAGE)
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise NotFound(EVENT_NOT_FOUND_ERROR_MESSAGE)
        # Verifica se o usuário tem permissão para acessar o evento
        self.check_object_permissions(self.request, event)
        return event
