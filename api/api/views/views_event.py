from typing import Optional
from django.contrib.auth.models import Group

from rest_framework import status, request, response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission

from ..views.base_views import BaseView
from api.models import Token, Event, Staff, Player
from ..serializers import EventSerializer, UserEventsSerializer
from ..utils import handle_400_error
from ..swagger import Errors, manual_parameter_event_id
from ..permissions import assign_permissions

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

TOKEN_NOT_PROVIDED_ERROR_MESSAGE = "Token não fornecido!"
TOKEN_NOT_FOUND_ERROR_MESSAGE = "Token não encontrado!"
TOKEN_ALREADY_USED_ERROR_MESSAGE = "Token já utilizado para criação de evento!"
EVENT_NOT_FOUND_ERROR_MESSAGE = "Nenhum evento encontrado!"
EVENT_DOES_NOT_EXIST_ERROR_MESSAGE = "Este evento não existe!"


# class TokenPermissions(BasePermission):
#     def has_permission(self, request, view):
#         if request.method == 'POST':
#             return request.user.has_perm('api.add_token')
#         if request.method == 'GET':
#             return request.user.has_perm('api.view_token')
#         if request.method == 'DELETE':
#             return request.user.has_perm('api.delete_token')


# class TokenView(BaseView):
#     permission_classes = [IsAuthenticated, TokenPermissions]

#     @swagger_auto_schema(

#         security=[{'Bearer': []}],
#         responses={200: openapi.Response(
#             'OK', TokenSerializer), **Errors([403]).retrieve_erros()}
#     )
#     def post(self, request):
#         """Cria um novo token e retorna o código do token gerado.

#         Permissões necessárias: IsAthenticated ,CanAddToken"""
#         if not request.user.has_perm('api.add_token'):
#             return response.Response(status=status.HTTP_403_FORBIDDEN)
#         token = Token.objects.create()
#         data = TokenSerializer(token).data
#         return response.Response(status=status.HTTP_200_OK, data=data)


class EventPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário tem a permissão 'delete_event' para o objeto específico
        if request.method == 'DELETE':
            return request.user.has_perm('api.delete_event', obj)
        if request.method == 'PUT':
            return request.user.has_perm('api.change_event', obj)


class EventView(BaseView):
    """Lida com os requests relacionados a eventos."""
    permission_classes = [IsAuthenticated, EventPermissions]

    @ swagger_auto_schema(
        tags=['event'],
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
            event = self.get_object_token()
        except Exception as e:
            return handle_400_error(str(e))

        self.check_object_permissions(request, event)
        event.delete()
        self.token.used = False
        self.token.save()
        return response.Response(status=status.HTTP_200_OK)

    @ swagger_auto_schema(
        tags=['event'],
        operation_summary="Retorna todos os eventos associados ao usuário logado e seu cargo no evento.",
        operation_description="""Retorna todos os eventos associados ao usuário logado. Retorna o cargo que o usuário possui no evento.
        Caso não haja eventos, retorna uma lista vazia.
        Os cargos que um usuário pode ter em um evento são: 'admin', 'manager', 'staff' e 'player'.
        Sempre o maior cargo do usuário é retornado. Ou seja, se o usuário é um _staff manager_ em um evento, o cargo retornado será apenas 'manager'.
        Se o usuário é um _staff_ em um evento, o cargo retornado será 'staff'.
        """,
        security=[{'Bearer': []}],
        responses={200: openapi.Response(
            'OK', UserEventsSerializer), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request, *args, **kwargs):
        """Retorna todos os eventos associados ao usuário que fez a requisição.
        E o cargo dele no evento.
        """
        events = request.user.events.all()
        data_to_serialize = []
        for event in events:
            if event.admin_email == request.user.email:
                data_to_serialize.append(
                    {'event': event, 'role': 'admin'})
                continue
            staff = Staff.objects.filter(
                event=event, user=request.user).first()
            if staff and staff.is_manager:
                data_to_serialize.append(
                    {'event': event, 'role': 'manager'})
                continue
            elif staff:
                data_to_serialize.append(
                    {'event': event, 'role': 'staff'})
                continue
            else:
                player = Player.objects.filter(
                    event=event, user=request.user).first()
                if player:
                    data_to_serialize.append(
                        {'event': event, 'role': 'player'})
        data = UserEventsSerializer(data_to_serialize, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    @ swagger_auto_schema(
        tags=['event'],
        operation_description=""" __Cria um novo evento associado a um token e retorna o evento criado.__
        Caso o evento já exista, retorna o evento existente. Isso foi feito para permitir novamente o login do adminsitrador do evento caso ele tenha fechado a aplicação ou feito logout.
        Por padrão, o evento possui *o mesmo email do usuário que o criou*. Caso outro usuário tente acessar o evento como administrador, *ele não terá permissão*.

        Status code 200 é retornado caso o evento já exista e o status code 201 é retornado caso o evento seja criado com sucesso.
        Status code 400 é retornado caso o token não seja fornecido ou não exista.
        Status code 403 é retornado caso o usuário que tenta acessar o evento não seja o administrador do evento.
        """,
        operation_summary="Cria um novo evento.",
        security=[{'Bearer': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token_code': openapi.Schema(type=openapi.TYPE_STRING, description='Código do token para criar um evento.'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do evento.')
            },
            required=['token_code', 'name']
        ),
        responses={200: openapi.Response(
            'OK', EventSerializer), 201: openapi.Response(
            'OK', EventSerializer), **Errors([400, 403]).retrieve_erros()}
    )
    def post(self, request, *args, **kwargs) -> response.Response:
        token_code: str = self.get_token_code(request)
        name: str = request.data.get('name')
        if token_code is not None and name is not None:
            token_code = token_code.strip()
            name = name.strip()
        if not token_code:
            return handle_400_error(TOKEN_NOT_PROVIDED_ERROR_MESSAGE)

        token = self.get_token(token_code)
        if not token:
            return handle_400_error(TOKEN_NOT_FOUND_ERROR_MESSAGE)

        if token.is_used():
            return handle_400_error(TOKEN_ALREADY_USED_ERROR_MESSAGE)

        event, created = self.get_or_create_event(token)
        if not event:
            return handle_400_error(EVENT_DOES_NOT_EXIST_ERROR_MESSAGE)
        if created:
            event.name = name

        response_status, data = self.handle_event_permissions(
            request, event, created)
        if response_status != status.HTTP_201_CREATED:
            return response.Response(status=response_status, data=data)

        self.assign_event_admin_permissions(request, event)

        return response.Response(status=status.HTTP_201_CREATED, data=data)

    @swagger_auto_schema(
        tags=['event'],
        operation_summary="Atualiza o nome do evento.",
        operation_description="Atualiza o nome do evento associado. Retorna o evento atualizado.",
        manual_parameters=manual_parameter_event_id,
        security=[{'Bearer': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do evento.')
            },
            required=['name']
        ),
        responses={200: openapi.Response(
            'OK', EventSerializer), **Errors([400]).retrieve_erros()}
    )
    def put(self, request: request.Request, *args, **kwargs) -> response.Response:
        if request.data is None or 'name' not in request.data:
            return handle_400_error("Nome do evento não fornecido!")
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        name = request.data['name']
        name = name.strip()
        event.name = name
        event.save()
        data = EventSerializer(event).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    def get_token_code(self, request):
        return request.data.get('token_code')

    def get_or_create_event(self, token):
        return Event.objects.get_or_create(token=token)

    def handle_event_permissions(self, request, event, created) -> tuple[int, dict]:
        data = EventSerializer(event).data
        if not created and request.user.email != event.admin_email:
            data = {'errors': 'Você não é o administrador deste evento.'}
            return status.HTTP_403_FORBIDDEN, data
        elif not created and request.user.email == event.admin_email:
            return status.HTTP_200_OK, data

        event.admin_email = request.user.email
        event.save()
        return status.HTTP_201_CREATED, data

    def assign_event_admin_permissions(self, request, event):
        group = Group.objects.get(name='event_admin')
        assign_permissions(user=request.user, group=group, event=event)
        request.user.events.add(event)

    def get_object_token(self) -> Event | Exception:
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
