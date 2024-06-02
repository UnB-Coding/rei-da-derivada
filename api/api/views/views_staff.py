from io import StringIO
import pandas as pd
from typing import Optional
from django.forms import ValidationError
from django.contrib.auth.models import Group

from rest_framework import status, request, response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from rest_framework.parsers import MultiPartParser

from api.models import Token, Event, Staff
from users.models import User
from ..serializers import EventSerializer, StaffSerializer, UploadFileSerializer
from .views_event import TOKEN_NOT_PROVIDED_ERROR_MESSAGE, TOKEN_NOT_FOUND_ERROR_MESSAGE, EVENT_NOT_FOUND_ERROR_MESSAGE
from ..utils import handle_400_error
from ..swagger import Errors
from ..permissions import assign_permissions

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


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
        Retorna o evento no qual o usuário foi adicionado.
        """,
        operation_summary="Adiciona um novo membro da equipe ao evento.",

        request_body=openapi.Schema(
            title='Token e Email do Monitor', type=openapi.TYPE_OBJECT,
            properties={'token_code': openapi.Schema(type=openapi.TYPE_STRING, description='Código do token', example='123456'),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email do monitor', example='example@email.com')},
            required=['token_code', 'email']),
        responses={200: openapi.Response(
            'OK', EventSerializer), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Adiciona um novo membro da equipe ao evento. O usuário será atribuido ao grupo 'staff_member'
        e terá permissões de Staff Member no evento associado ao token fornecido.

        """
        if request.data is None or 'token_code' not in request.data or 'email' not in request.data:
            return handle_400_error('Dados inválidos!')
        token_code = request.data['token_code']
        if not token_code:
            return handle_400_error(TOKEN_NOT_PROVIDED_ERROR_MESSAGE)
        email = request.data['email']
        if not email:
            return handle_400_error('Email não fornecido!')
        token = self.get_token(token_code)
        if not token:
            return handle_400_error(TOKEN_NOT_FOUND_ERROR_MESSAGE)
        event = self.get_event_by_token(token)
        if not event:
            return handle_400_error(EVENT_NOT_FOUND_ERROR_MESSAGE)
        staff = Staff.objects.filter(
            registration_email=email, event=event).first()
        if not staff:
            return handle_400_error('Este email não está cadastrado como monitor para este evento.')
        if staff.user is None:
            staff.user = request.user
        elif staff.user != request.user:
            return response.Response(status=status.HTTP_403_FORBIDDEN, data='Este email já está cadastrado como monitor para este evento.')

        group = Group.objects.get(name='staff_member')
        request.user.groups.add(group)
        request.user.events.add(event)
        assign_permissions(user=request.user, group=group, event=event)
        data = EventSerializer(event).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    @swagger_auto_schema(
        operation_description="""Retorna os todos usuários monitores associados ao evento.
        Procura por todos os objetos staff associados ao evento e retorna esses objetos.
        """,
        operation_summary="Retorna os usuários monitores associados ao evento.",
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, description='ID do evento', type=openapi.TYPE_INTEGER)],
        responses={200: openapi.Response(
            'OK', StaffSerializer), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Retorna os usuários staff_member associados ao evento."""
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        # users = event.users.filter(groups__name='staff_member').exclude(
        #     groups__name='staff_manager').exclude(groups__name='app_admin').exclude(groups__name='event_admin')
        staffs = event.staff.filter(is_manager=False)
        data = StaffSerializer(staffs, many=True).data
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


class AddStaffManagerPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return request.user.has_perm('api.change_event', obj)
        return False


class AddStaffManager(APIView):
    permission_classes = [IsAuthenticated, AddStaffManagerPermissions]

    @swagger_auto_schema(
        operation_description="""Promove um usuário monitor a Gerente de Equipe no evento associado.
        Deve ser enviado o email do usuário a ser promovido a Gerente de Equipe. Quem envia a requisição é o Admin do evento.
        """,
        operation_summary="Promove um monitor a Gerente de Equipe.",
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, description='ID do evento', type=openapi.TYPE_INTEGER)],
        request_body=openapi.Schema
        (title='Email do Usuário', type=openapi.TYPE_OBJECT,
         properties={'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email do usuário', example='example@email.com')}),
        responses={200: openapi.Response(
            "Gerente de equipe adicionado com sucesso!'"), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs):
        """Promove um usuário a staff_manager no evento associado.
        """
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        try:
            staff_user = self.get_request_user()
        except Exception as e:
            return handle_400_error(str(e))
        staff_object = Staff.objects.filter(
            user=staff_user, event=event).first()
        if not staff_object:
            return handle_400_error('O usuário não é monitor deste evento!')
        staff_object.is_manager = True
        staff_object.save()
        group = Group.objects.get(name='staff_manager')
        staff_user.groups.add(group)
        staff_user.events.add(event)
        assign_permissions(user=staff_user, group=group, event=event)
        return response.Response(status=status.HTTP_200_OK, data='Gerente de equipe adicionado com sucesso!')

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

    def get_request_user(self):
        if 'email' not in self.request.data:
            raise ValidationError('Email do Usuário não fornecido!')
        email = self.request.data['email']
        if not email:
            raise ValidationError('Email do Usuário não fornecido!')
        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError('Usuário não encontrado!')
        else:
            return user


class AddStaffPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return request.user.has_perm('api.change_event', obj)
        return False


class AddStaffMembers(APIView):
    permission_classes = [IsAuthenticated, AddStaffPermissions]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description='Adiciona monitores ao evento através do excel fornecido pelo administrador.',
        operation_summary='Adiciona multiplos monitores ao evento.',
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Id do evento')],
        request_body=UploadFileSerializer,
        responses={201: openapi.Response(
            201), **Errors([400]).retrieve_erros()})
    def post(self, request: request.Request, *args, **kwargs):
        try:
            event = self.get_object()
        except ValidationError as e:
            return handle_400_error(str(e))

        self.check_object_permissions(self.request, event)

        try:
            excel_file = self.get_excel_file()
        except ValidationError as e:
            return handle_400_error(str(e))
        extension = (excel_file.name.split("."))[1]
        df = self.createData(extension=extension, file=excel_file)
        if df is None:
            return handle_400_error('Arquivo inválido!')
        self.create_staff(df, event)
        return response.Response(status=status.HTTP_201_CREATED, data='Monitores adicionados com sucesso!')

    def create_staff(self, df: pd.DataFrame, event: Event) -> None:
        process_data = ['Nome Completo', 'E-mail']
        df_needed = df[process_data]

        for i, line in df_needed.iterrows():
            name = line['Nome Completo']
            email = line['E-mail']
            staff, created = Staff.objects.get_or_create(
                full_name=name, registration_email=email, event=event)
            if not created:
                staff.full_name = name
                staff.registration_email = email
                staff.save()

    def createData(self, extension, file) -> Optional[pd.DataFrame]:
        data = None
        if extension == 'csv':
            file_data = file.read().decode('utf-8')
            csv_data = StringIO(file_data)
            data = pd.read_csv(csv_data, header=0, encoding='utf-8')

        elif extension == 'xlsx' or extension == 'xls':
            data = pd.read_excel(file)
        return data

    def get_excel_file(self):
        excel_file = self.request.data['file']
        if not excel_file:
            raise ValidationError('Arquivo não encontrado!')
        if not excel_file.name:
            raise ValidationError('Arquivo inválido!')
        return excel_file

    def get_object(self):
        if 'event_id' not in self.request.query_params:
            raise ValidationError('Dados inválidos!')

        event_id = self.request.query_params.get('event_id')
        if not event_id:
            raise ValidationError('event_id é obrigatório!')
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise ValidationError('Evento não encontrado!')
        return event
