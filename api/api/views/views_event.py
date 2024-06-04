from typing import Optional
from django.contrib.auth.models import Group

from rest_framework import status, request, response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission

from api.models import Token, Event
from users.models import User
from ..serializers import EventSerializer, TokenSerializer
from ..utils import handle_400_error
from ..swagger import Errors
from ..permissions import assign_permissions

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

TOKEN_NOT_PROVIDED_ERROR_MESSAGE = "Token não fornecido!"
TOKEN_NOT_FOUND_ERROR_MESSAGE = "Token não encontrado!"
TOKEN_ALREADY_USED_ERROR_MESSAGE = "Token já utilizado para criação de evento!"
EVENT_NOT_FOUND_ERROR_MESSAGE = "Nenhum evento encontrado!"
EVENT_DOES_NOT_EXIST_ERROR_MESSAGE = "Este evento não existe!"


class TokenPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.has_perm('api.add_token')
        if request.method == 'GET':
            return request.user.has_perm('api.view_token')
        if request.method == 'DELETE':
            return request.user.has_perm('api.delete_token')


class TokenView(APIView):
    permission_classes = [IsAuthenticated, TokenPermissions]

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
    def has_object_permission(self, request, view, obj):
        # Se o usuário pertence ao grupo 'App_admin', conceda total permissão
        if Group.objects.get(name='app_admin') in request.user.groups.all():
            return True

        # Verifica se o usuário tem a permissão 'delete_event' para o objeto específico
        if request.method == 'DELETE':
            return request.user.has_perm('api.delete_event', obj)


class EventView(APIView):
    """Lida com os requests relacionados a eventos."""
    permission_classes = [IsAuthenticated, EventPermissions]

    def get_object(self) -> Event | Exception:
        token_code = self.request.data.get('token_code')
        if not token_code:
            raise Exception(TOKEN_NOT_PROVIDED_ERROR_MESSAGE)
        self.token = self.get_token(token_code)
        if not self.token:
            raise Exception(TOKEN_NOT_FOUND_ERROR_MESSAGE)
        event = self.get_event_by_token(self.token)
        if not event:
            raise Exception(EVENT_NOT_FOUND_ERROR_MESSAGE)
        return event

    def get_token(self, token_code: str) -> Optional[Token]:
        """Retorna um token com o código fornecido."""
        return Token.objects.filter(
            token_code=token_code).first()

    def get_event_by_token(self, token: Token) -> Optional[Event]:
        """Retorna um evento com o código fornecido."""
        return Event.objects.filter(
            token=token).first()

    def token_code_exists(self, token_code: str) -> bool:
        """Verifica se o código do token fornecido na requisição é válido."""
        if len(token_code) == 0 or token_code.isspace():
            return False
        return True

    @ swagger_auto_schema(
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
    def post(self, request, *args, **kwargs) -> response.Response:
        """Cria um novo evento associado a um token e retorna o evento criado.
        Caso o token já tenha sido utilizado ou já exista um evento associado ao token, retorna um erro 400.

        Permissões necessárias: IsAthenticated ,EventPermissions
        """

        if 'token_code' not in request.data:
            return handle_400_error(TOKEN_NOT_PROVIDED_ERROR_MESSAGE)

        token_code = request.data['token_code']

        if not self.token_code_exists(token_code):
            return handle_400_error(TOKEN_NOT_FOUND_ERROR_MESSAGE)

        token = self.get_token(token_code)

        if not token:
            return handle_400_error(TOKEN_NOT_FOUND_ERROR_MESSAGE)

        if token.is_used():
            return handle_400_error(TOKEN_ALREADY_USED_ERROR_MESSAGE)

        event, created = Event.objects.get_or_create(token=token)
        group = Group.objects.get(name='event_admin')
        token.mark_as_used()
        try:
            assign_permissions(user=request.user, group=group, event=event)
        except Exception as e:
            return handle_400_error(str(e))
        data = EventSerializer(event).data

        return response.Response(status=status.HTTP_201_CREATED, data=data)

    @ swagger_auto_schema(
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
    def delete(self, request: request.Request, *args, **kwargs):
        """Deleta um evento associado a um token e retorna o evento deletado.

        Caso o token não tenha um evento associado, retorna um erro 400.

        Permissões necessárias: IsAthenticated ,EventPermissions
        """
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))

        self.check_object_permissions(request, event)
        event.delete()
        self.token.used = False
        self.token.save()
        return response.Response(status=status.HTTP_200_OK)

    @ swagger_auto_schema(
        operation_summary="Retorna todos os eventos associados ao usuário logado.",
        operation_description='Retorna todos os eventos associados ao usuário logado. Caso não haja eventos, retorna uma lista vazia.',
        security=[{'Bearer': []}],
        responses={200: openapi.Response(
            'OK', EventSerializer), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request, *args, **kwargs):
        """Retorna todos os eventos associados ao usuário que fez a requisição."""
        events = request.user.events.all()
        data = EventSerializer(events, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)
