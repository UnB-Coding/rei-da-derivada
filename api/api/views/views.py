from typing import Optional
from rest_framework import status, request, response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.models import Token, Event, Sumula, PlayerScore, Player
from users.models import User
from ..serializers import TokenSerializer, EventSerializer, PlayerSerializer, PlayerScoreSerializer, SumulaSerializer, UserSerializer
from rest_framework.permissions import BasePermission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ..utils import handle_400_error
from ..swagger import Errors
TOKEN_NOT_PROVIDED_ERROR_MESSAGE = "Token não fornecido!"
TOKEN_ERROR_MESSAGE = "Token não encontrado!"
EVENT_CREATE_ERROR_MESSAGE = "Evento não encontrado!"
EVENT_DELETE_ERROR_MESSAGE = "Este evento não existe!"


class CanAddToken(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.has_perm('api.add_token')
        return True


class TokenView(APIView):
    permission_classes = [IsAuthenticated, CanAddToken]

    @swagger_auto_schema(

        security=[{'Bearer': []}],
        responses={200: openapi.Response(
            'OK', TokenSerializer), **Errors([403]).retrieve_erros()}
    )
    def post(self, request):
        """Cria um novo token e retorna o código do token gerado.

        Permissões necessárias: IsAthenticated ,CanAddToken"""
        if not request.user.has_perm('api.add_token'):
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        token = Token.objects.create()
        data = TokenSerializer(token).data
        return response.Response(status=status.HTTP_200_OK, data=data)


class EventPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.has_perm('api.view_event')
        elif request.method == 'POST':
            return request.user.has_perm('api.add_event')
        elif request.method == 'PUT':
            return request.user.has_perm('api.change_event')
        elif request.method == 'DELETE':
            return request.user.has_perm('api.delete_event')
        return True


class EventView(APIView):
    """Lida com os requests relacionados a eventos."""
    permission_classes = [IsAuthenticated, EventPermissions]

    def get_permission_required(self):
        if self.request.method == 'POST':
            return ['api.add_event']
        elif self.request.method == 'DELETE':
            return ['api.delete_event']
        else:
            return []

    def get_token(self, token_code: str) -> Optional[Token]:
        """Retorna um token com o código fornecido."""
        return Token.objects.filter(
            token_code=token_code).first()

    def get_event(self, token: Token) -> Optional[Event]:
        """Retorna um evento com o código fornecido."""
        return Event.objects.filter(
            token=token).first()

    def token_code_exists(self, token_code: str) -> bool:
        """Verifica se o código do token fornecido na requisição é válido."""
        if len(token_code) == 0 or token_code.isspace():
            return False
        return True

    @swagger_auto_schema(
        operation_description="Cria um novo evento associado a um token e retorna o evento criado.",
        operation_summary="Cria um novo evento.",
        security=[{'Bearer': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token_code': openapi.Schema(type=openapi.TYPE_STRING, description='Código do token para criar um evento.')
            },
            required=['token_code']
        ),
        responses={200: openapi.Response(
            'OK', EventSerializer), **Errors([400]).retrieve_erros()}
    )
    def post(self, request, *args, **kwargs):
        """Cria um novo evento associado a um token e retorna o evento criado.
        Caso o token já tenha sido utilizado ou já exista um evento associado ao token, retorna um erro 400.

        Permissões necessárias: IsAthenticated ,EventPermissions
        """
        if 'token_code' not in request.data:
            return handle_400_error(TOKEN_NOT_PROVIDED_ERROR_MESSAGE)

        token_code = request.data['token_code']

        if not self.token_code_exists(token_code):
            return handle_400_error(TOKEN_ERROR_MESSAGE)

        token = self.get_token(token_code)

        if not token or token.is_used():
            return handle_400_error(TOKEN_ERROR_MESSAGE)

        if self.get_event(token):
            return handle_400_error(EVENT_CREATE_ERROR_MESSAGE)

        event = Event.objects.create(token=token)
        data = EventSerializer(event).data

        return response.Response(status=status.HTTP_201_CREATED, data=data)

    @swagger_auto_schema(
        operation_summary="Deleta um evento associado a um token.",
        operation_description='Deleta um evento associado a um token.',
        security=[{'Bearer': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token_code': openapi.Schema(type=openapi.TYPE_STRING, description='Código do token')
            },
            required=['token_code']
        ),
        responses={200: openapi.Response(
            'OK', EventSerializer), **Errors([400]).retrieve_erros()}
    )
    def delete(self, request, *args, **kwargs):
        """Deleta um evento associado a um token e retorna o evento deletado.
        Caso o token não tenha um evento associado, retorna um erro 400.

        Permissões necessárias: IsAthenticated ,EventPermissions
        """
        if 'token_code' not in request.data:
            return handle_400_error(TOKEN_NOT_PROVIDED_ERROR_MESSAGE)

        token_code = request.data['token_code']

        if not self.token_code_exists(token_code):
            return handle_400_error(TOKEN_ERROR_MESSAGE)

        token = self.get_token(token_code)
        if not token:
            return handle_400_error(TOKEN_ERROR_MESSAGE)
        event = self.get_event(token)
        if not event:
            return handle_400_error(EVENT_DELETE_ERROR_MESSAGE)
        event.delete()
        token.used = False
        return response.Response(status=status.HTTP_200_OK)


class CanViewPlayers(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.has_perm('api.view_player')
        return True


class GetAllPlayersView(APIView):

    permission_classes = [IsAuthenticated, CanViewPlayers]

    @ swagger_auto_schema(security=[{'Bearer': []}],
                          manual_parameters=[openapi.Parameter(
                              'event_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Id do evento')],
                          responses={200: openapi.Response(200, PlayerSerializer), **Errors([400]).retrieve_erros()})
    def get(self, request: request.Request, *args, **kwargs):
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
