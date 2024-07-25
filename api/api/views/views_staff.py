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

from ..views.base_views import BaseView
from api.models import Token, Event, Staff
from users.models import User
from ..serializers import EventSerializer, StaffSerializer, UploadFileSerializer, StaffLoginSerializer
from .views_event import TOKEN_NOT_PROVIDED_ERROR_MESSAGE, TOKEN_NOT_FOUND_ERROR_MESSAGE, EVENT_NOT_FOUND_ERROR_MESSAGE
from ..utils import handle_400_error
from ..swagger import Errors, manual_parameter_event_id
from ..permissions import assign_permissions

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.core.files.uploadedfile import UploadedFile


class StaffPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method == 'GET':
            return request.user.has_perm('api.add_sumula_event', obj)
        return False


class StaffView(BaseView):
    permission_classes = [IsAuthenticated, StaffPermissions]

    def get_token(self, token_code: str) -> Optional[Token]:
        """Retorna um token com o código-token fornecido."""
        return Token.objects.filter(token_code=token_code).first()

    @ swagger_auto_schema(
        tags=['staff'],
        operation_description="""Realiza o login de um membro da equipe ao evento.
        O usuário terá permissões de Monitor no evento associado ao token fornecido.
        Retorna objeto STAFF associado ao usuario e o evento.
        Para a verificacao de rotas no front-end pode-se usar o parametro de 'is_manager' do objeto retornado.
        """,
        operation_summary="Realiza o login de um membro da equipe ao evento.",

        request_body=openapi.Schema(
            title='Token de join do Evento', type=openapi.TYPE_OBJECT,
            properties={'join_token': openapi.Schema(
                type=openapi.TYPE_STRING, description='Código do token', example='123456')},
            required=['join_token']),
        responses={200: openapi.Response(
            'OK', StaffLoginSerializer), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Adiciona um novo membro da equipe ao evento. O usuário será atribuido ao grupo 'staff_member'
        e terá permissões de Staff Member no evento associado ao token fornecido.

        """
        if request.data is None or 'join_token' not in request.data:
            return handle_400_error('Dados inválidos!')
        token = request.data['join_token']
        if not token:
            return handle_400_error(TOKEN_NOT_PROVIDED_ERROR_MESSAGE)
        event = Event.objects.filter(join_token=token).first()
        if not event:
            return handle_400_error(EVENT_NOT_FOUND_ERROR_MESSAGE)
        staff = Staff.objects.filter(
            registration_email=request.user.email, event=event).first()
        if not staff:
            return handle_400_error('Este email não está cadastrado como monitor para este evento.')
        if not staff.user:
            staff.user = request.user
            group = None
            if staff.is_manager:
                group = Group.objects.get(name='staff_manager')
            else:
                group = Group.objects.get(name='staff_member')
            assign_permissions(user=request.user, group=group, event=event)
        request.user.events.add(event)
        staff.save()
        data = StaffLoginSerializer(staff).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    @ swagger_auto_schema(
        tags=['staff'],
        operation_description="""Retorna os todos usuários monitores associados ao evento.
        Procura por todos os objetos staff associados ao evento e retorna esses objetos.

        Para a diferenciação entre monitores e gerentes de equipe, é necessário verificar o campo 'is_manager' de cada objeto retornado.
        """,
        operation_summary="Retorna todos os usuários monitores associados ao evento.",
        manual_parameters=manual_parameter_event_id,
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
        staffs = event.staff.all()
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


class AddStaffManager(BaseView):
    permission_classes = [IsAuthenticated, AddStaffManagerPermissions]

    @ swagger_auto_schema(
        tags=['staff'],
        operation_description="""Promove um usuário monitor a Gerente de Equipe no evento associado.
        Deve ser enviado o email do usuário a ser promovido a Gerente de Equipe. Quem envia a requisição é o Admin do evento.
        """,
        operation_summary="Promove um monitor a Gerente de Equipe.",
        manual_parameters=manual_parameter_event_id,
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


class AddStaffMembers(BaseView):
    permission_classes = [IsAuthenticated, AddStaffPermissions]
    parser_classes = [MultiPartParser]

    @ swagger_auto_schema(
        tags=['staff'],
        operation_description='Adiciona monitores ao evento através do excel fornecido pelo administrador.',
        operation_summary='Adiciona multiplos monitores ao evento.',
        manual_parameters=manual_parameter_event_id,
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
        if not isinstance(excel_file, UploadedFile):
            raise ValidationError('Arquivo inválido!')
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


class AddSingleStaff(BaseView):
    permission_classes = [IsAuthenticated, AddStaffPermissions]

    @swagger_auto_schema(
        tags=['staff'],
        operation_description="""Adiciona um monitor manualmente ao evento.
            Devem ser enviados os dados do monitor a ser adicionado.
                Obrigatório: Nome Completo, E-mail e se é Gerente de Equipe ou não.""",
        operation_summary='Adiciona um monitor manualmente ao evento.',
        manual_parameters=manual_parameter_event_id,
        request_body=openapi.Schema(
            title='Dados do Monitor', type=openapi.TYPE_OBJECT,
            properties={'full_name': openapi.Schema(
                type=openapi.TYPE_STRING, description='Nome Completo', example='João da Silva'),
                'registration_email': openapi.Schema(
                type=openapi.TYPE_STRING, description='E-mail', example='joao@email.com'),
                'is_manager': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Gerente de Equipe', example=False)}),
        required=['full_name', 'registration_email', 'is_manager'],
        responses={201: openapi.Response(
            'Monitor adicionado com sucesso!'), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs):
        if request.data is None or 'full_name' not in request.data or 'registration_email' not in request.data or 'is_manager' not in request.data:
            return handle_400_error('Dados inválidos!')
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))

        self.check_object_permissions(self.request, event)
        full_name = request.data['full_name']
        registration_email = request.data['registration_email']
        is_manager = request.data['is_manager']
        staff, created = Staff.objects.get_or_create(
            full_name=full_name, registration_email=registration_email, event=event, is_manager=is_manager)
        if not created:
            return handle_400_error('Monitor já cadastrado para este evento!')

        return response.Response(status=status.HTTP_201_CREATED, data='Monitor adicionado com sucesso!')


class EditStaffData(BaseView):
    permission_classes = [IsAuthenticated, AddStaffPermissions]

    @swagger_auto_schema(
        tags=['staff'],
        operation_description="""Edita os dados de um monitor do evento.
            Devem ser enviados os dados do monitor a ser editado.
            Obrigatório: Nome Completo, E-mail e se é Gerente de Equipe ou não.
            Esta rota permite que o nome de um monitor seja alterado e se ele é gerente de equipe ou não.
                """,
        operation_summary='Edita os dados de um monitor do evento.',
        manual_parameters=manual_parameter_event_id,
        request_body=openapi.Schema(
            title='Dados do Monitor', type=openapi.TYPE_OBJECT,
            properties={
                'full_name': openapi.Schema(
                    type=openapi.TYPE_STRING, description='Nome Completo', example='João da Silva'),
                'registration_email': openapi.Schema(
                    type=openapi.TYPE_STRING, description='E-mail atual do monitor', example='joao@email.com'),
                'is_manager': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Gerente de Equipe', example=False),
                'new_email': openapi.Schema(type=openapi.TYPE_STRING, description='Novo e-mail do monitor', example='joao1234@outroemail.com')
            }
        ),
        required=['registration_email'],
        responses={200: openapi.Response(
            'Monitor editado com sucesso!'), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs):
        if request.data is None or 'full_name' not in request.data or 'registration_email' not in request.data or 'is_manager' not in request.data or 'new_email' not in request.data:
            return handle_400_error('Dados inválidos!')
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))

        self.check_object_permissions(self.request, event)
        full_name = request.data['full_name']
        registration_email = request.data['registration_email']
        new_email = request.data['new_email']
        is_manager = request.data['is_manager']
        staff = Staff.objects.filter(
            registration_email=registration_email, event=event).first()
        if not staff:
            return handle_400_error('Monitor não encontrado para este evento!')
        staff.is_manager = is_manager
        staff.full_name = full_name
        staff.registration_email = new_email
        staff.save()
        return response.Response(status=status.HTTP_200_OK, data='Monitor editado com sucesso!')
