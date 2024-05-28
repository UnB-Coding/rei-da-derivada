from typing import Optional
from django.forms import ValidationError
from rest_framework import status, request, response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.models import Token, Event
from ..serializers import TokenSerializer, EventSerializer, UserSerializer
from rest_framework.permissions import BasePermission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ..utils import handle_400_error
from ..swagger import Errors
from django.contrib.auth.models import Group
from ..permissions import assign_permissions
from guardian.shortcuts import get_perms, remove_perm, assign_perm

TOKEN_NOT_PROVIDED_ERROR_MESSAGE = "Token não fornecido!"
TOKEN_NOT_FOUND_ERROR_MESSAGE = "Token não encontrado!"
TOKEN_ALREADY_USED_ERROR_MESSAGE = "Token já utilizado para criação de evento!"
EVENT_NOT_FOUND_ERROR_MESSAGE = "Evento não encontrado!"
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


class StaffPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if Group.objects.get(name='app_admin') in request.user.groups.all():
            return True
        if request.method == 'GET':
            return request.user.has_perm('api.change_event', obj)
        return False


class StaffView(APIView):
    permission_classes = [IsAuthenticated, StaffPermissions]

    def get_token(self, token_code: str) -> Optional[Token]:
        """Retorna um token com o código-token fornecido."""
        return Token.objects.filter(token_code=token_code).first()

    def get_event_by_token(self, token: Token) -> Optional[Event]:
        """Retorna um evento com o token fornecido."""
        return Event.objects.filter(token=token).first()

    @ swagger_auto_schema(
        operation_description="""Adiciona um novo membro da equipe ao evento.
        O usuário terá permissões de Monitor no evento associado ao token fornecido.
        """,
        operation_summary="Adiciona um novo membro da equipe ao evento.",
        operation_id="add_staff_member",
        request_body=TokenSerializer,
        responses={200: openapi.Response(
            'OK'), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Adiciona um novo membro da equipe ao evento. O usuário será atribuido ao grupo 'staff_member' e terá permissões de Staff Member no evento associado ao token fornecido.
        """
        if request.data is None or 'token_code' not in request.data:
            return handle_400_error(TOKEN_NOT_PROVIDED_ERROR_MESSAGE)
        token_code = request.data['token_code']
        if not token_code:
            return handle_400_error(TOKEN_NOT_PROVIDED_ERROR_MESSAGE)

        token = self.get_token(token_code)
        if not token:
            return handle_400_error(TOKEN_NOT_FOUND_ERROR_MESSAGE)
        event = self.get_event_by_token(token)
        if not event:
            return handle_400_error(EVENT_NOT_FOUND_ERROR_MESSAGE)

        group = Group.objects.get(name='staff_member')
        request.user.groups.add(group)
        request.user.events.add(event)
        assign_permissions(user=request.user, group=group, event=event)

        return response.Response(status=status.HTTP_200_OK, data={'message': 'Membro da equipe adicionado com sucesso!'})

    @swagger_auto_schema(
        operation_description="""Retorna os todos usuários monitores associados ao evento.
        """,
        operation_summary="Retorna os usuários monitores associados ao evento.",
        operation_id="get_staff_members",
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, description='ID do evento', type=openapi.TYPE_INTEGER)],
        responses={200: openapi.Response(
            'OK', UserSerializer), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Retorna os usuários staff_member associados ao evento."""
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        users = event.users.filter(groups__name='staff_member').exclude(
            groups__name='staff_manager').exclude(groups__name='app_admin').exclude(groups__name='event_admin')
        data = UserSerializer(users, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    def get_object(self):
        if 'event_id' not in self.request.query_params:
            raise ValidationError('Evento não fornecido!')
        event_id = self.request.query_params['event_id']
        if not event_id:
            raise ValidationError('Evento não fornecido!')
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise ValidationError('Evento não encontrado!')
        return event
