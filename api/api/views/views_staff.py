from io import StringIO
import os
import pandas as pd
from typing import Optional
from django.forms import ValidationError
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
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
        if request.method == 'PUT':
            return request.user.has_perm('api.change_event', obj)
        if request.method == 'DELETE':
            return request.user.has_perm('api.delete_event', obj)
        return False


class StaffView(BaseView):
    permission_classes = [IsAuthenticated, StaffPermissions]

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
        token = token.strip()
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
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        staffs = event.staff.all()
        data = StaffSerializer(staffs, many=True).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    @swagger_auto_schema(
        tags=['staff'],
        operation_description="""Edita os dados de um monitor do evento.,
        É permitido editar o **nome completo,email do staff e se é gerente ou não**.
        **Deve ser fornecido no request_body o email atual do staff** e os campos que deseja alterar:
        - registration_email: Email atual do staff
        - full_name: Nome completo do staff
        - new_email: Novo email do stagg
        - is_manager: Se é gerente de equipe ou não
        - clear_user: Limpar usuário associado ao monitor, caso deseje remover a relação com o usuário.
        Note que as chaves do request_body devem ser passadas, porém o valor pode ser vazio, **exceto do campo is_manager, que deve ser bool**.""",
        operation_summary='Edita os dados de um monitor do evento.',
        manual_parameters=manual_parameter_event_id,
        request_body=openapi.Schema(
            title='Dados do Monitor', type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do objeto Staff', example=1),
                'full_name': openapi.Schema(
                    type=openapi.TYPE_STRING, description='Nome Completo', example='João da Silva'),
                'is_manager': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Gerente de Equipe', example=False),
                'new_email': openapi.Schema(type=openapi.TYPE_STRING, description='Novo e-mail do monitor', example='joao1234@outroemail.com'),
                'clear_user': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Limpar usuário associado ao monitor', example=False)
            }
        ),
        required=['registration_email'],
        responses={200: openapi.Response(
            'Monitor editado com sucesso!'), **Errors([400]).retrieve_erros()}
    )
    def put(self, request: request.Request, *args, **kwargs):
        required_fields = ['id', 'full_name', 'new_email', 'is_manager']
        if not all(field in request.data for field in required_fields):
            return handle_400_error('Dados inválidos!')
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        staff_id = request.data['id']
        if not staff_id:
            return handle_400_error('ID do monitor não fornecido!')
        staff = Staff.objects.filter(id=staff_id).first()
        if not staff:
            return handle_400_error('Monitor não encontrado para este evento!')
        full_name = request.data['full_name']
        new_email = request.data['new_email']
        is_manager = request.data['is_manager']
        clear_user = request.data.get('clear_user', False)
        if not isinstance(is_manager, bool):
            return handle_400_error('is_manager deve ser um booleano!')
        if full_name:
            full_name = full_name.strip()
            for word in full_name.split():
                full_name = full_name.replace(word, word.capitalize())
        if new_email:
            try:
                validate_email(new_email)
            except Exception:
                return handle_400_error('Email inválido!')
        staff.is_manager = is_manager
        staff.full_name = full_name
        staff.registration_email = new_email
        if clear_user:
            staff.user = None
            staff.save()
            return response.Response(status=status.HTTP_200_OK, data='Monitor editado com sucesso e relação com usuário removida!')
        staff.save()
        return response.Response(status=status.HTTP_200_OK, data='Monitor editado com sucesso!')

    @swagger_auto_schema(
        tags=['staff'],
        operation_description="""Deleta um monitor associado ao evento.
        Deve ser fornecido o ID do monitor a ser deletado. Após a deleção, o monitor não terá mais acesso ao evento.
        Apenas o Admin do evento pode realizar essa ação.""",
        operation_summary='Deleta um monitor associado ao evento.',
        manual_parameters=manual_parameter_event_id,
        request_body=openapi.Schema(
            title='ID do Monitor', type=openapi.TYPE_OBJECT,
            properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do monitor', example=1)}),
        required=['id'],
        responses={200: openapi.Response(
            'Monitor deletado com sucesso!'), **Errors([400]).retrieve_erros()}
    )
    def delete(self, request: request.Request, *args, **kwargs):
        if 'id' not in request.data:
            return handle_400_error('ID do monitor não fornecido!')
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        staff_id = request.data['id']
        if not staff_id:
            return handle_400_error('ID do monitor não fornecido!')
        staff = Staff.objects.filter(id=staff_id).first()
        if not staff:
            return handle_400_error('Monitor não encontrado para este evento!')
        staff.delete()
        return response.Response(status=status.HTTP_200_OK, data='Monitor deletado com sucesso!')


class AddStaffManagerPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return request.user.has_perm('api.change_event', obj)
        return False


class AddStaffManager(BaseView):
    permission_classes = [IsAuthenticated, AddStaffManagerPermissions]

    @ swagger_auto_schema(
        tags=['staff'],
        operation_description="""Promove um monitor a Gerente de Equipe no evento associado.
        Deve ser enviado o email do monitor a ser promovido a Gerente de Equipe. Quem envia a requisição é o Admin do evento.
        """,
        operation_summary="Promove um monitor a Gerente de Equipe.",
        manual_parameters=manual_parameter_event_id,
        request_body=openapi.Schema
        (title='Email do Staff', type=openapi.TYPE_OBJECT,
         properties={'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email do staff', example='example@email.com')}),
        responses={200: openapi.Response(
            "Gerente de equipe adicionado com sucesso!'"), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs):
        """Promove um usuário a staff_manager no evento associado.
        """
        if 'email' not in self.request.data:
            raise ValidationError('Email do Usuário não fornecido!')
        email = self.request.data['email']
        if not email:
            return handle_400_error('Email do Usuário não fornecido!')
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)

        staff_object = Staff.objects.filter(
            registration_email=email, event=event).first()
        if not staff_object:
            return handle_400_error('O usuário não é monitor deste evento!')
        user = staff_object.user
        if staff_object.user:
            user.events.add(event)
            group = Group.objects.get(name='staff_manager')
            assign_permissions(user=user, group=group, event=event)
        staff_object.is_manager = True
        staff_object.save()
        return response.Response(status=status.HTTP_200_OK, data='Gerente de equipe adicionado com sucesso!')


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
            event = self.get_event()
        except ValidationError as e:
            return handle_400_error(str(e))

        self.check_object_permissions(self.request, event)

        try:
            excel_file = self.get_excel_file()
        except ValidationError as e:
            return handle_400_error(str(e))
        extension = os.path.splitext(excel_file.name)[-1].lower().strip('.')
        df = self.createData(extension=extension, file=excel_file)
        if df is None:
            return handle_400_error('Arquivo inválido!')

        try:
            errors_count, staff_count = self.create_staff(df, event)
        except Exception as e:
            return handle_400_error(str(e))
        if errors_count > 0 and errors_count < staff_count:
            return response.Response(status=status.HTTP_201_CREATED, data={
                'message': 'Monitores adicionados com sucesso!',
                'errors': f'{errors_count} monitores não foram adicionados devido a e-mail inválido. Verfique os e-mails dos monitores e tente novamente.'
            })
        elif errors_count == staff_count:
            return handle_400_error('Nenhum monitor foi adicionado! Verifique os dados de e-mail dos monitores e tente novamente')

        return response.Response(status=status.HTTP_201_CREATED, data='Monitores adicionados com sucesso!')

    def create_staff(self, df: pd.DataFrame, event: Event) -> tuple:
        process_data = ['nome completo', 'e-mail']
        df.columns = df.columns.str.strip().str.lower()
        # Verificar se as colunas necessárias estão presentes
        missing_columns = [
            col for col in process_data if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"ERRO - Colunas ausentes no arquivo: {', '.join(missing_columns)}")

        df_needed = df[process_data]
        errors_count = 0
        staff_count = 0
        for i, line in df_needed.iterrows():
            name = line['nome completo']
            email = line['e-mail']
            name, email = self.treat_name_and_email_excel(name, email)
            staff_count += 1
            try:
                validate_email(email)
            except:
                errors_count += 1
                continue
            staff, created = Staff.objects.get_or_create(
                registration_email=email, event=event)
            staff.full_name = name
            staff.save()
        return errors_count, staff_count

    def createData(self, extension, file) -> Optional[pd.DataFrame]:
        data = None
        if extension == 'csv':
            csv_data, encoding = self.treat_csv(file)
            delimiter = self.get_delimiter(csv_data)
            data = pd.read_csv(csv_data, header=0,
                               encoding=encoding, delimiter=delimiter)
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


class AddSingleStaff(BaseView):
    permission_classes = [IsAuthenticated, AddStaffPermissions]

    @ swagger_auto_schema(
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
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))

        self.check_object_permissions(self.request, event)
        full_name = request.data['full_name']
        registration_email = request.data['registration_email']
        is_manager = request.data['is_manager']
        if not full_name or not registration_email:
            return handle_400_error('Nome Completo e email são obrigaórios!')
        if is_manager not in [True, False]:
            return handle_400_error('is_manager deve ser um booleano!')
        staff, created = Staff.objects.get_or_create(
            registration_email=registration_email, event=event)
        if not created:
            return handle_400_error('Monitor já cadastrado com este e-mail para este evento!')
        full_name = full_name.strip()
        for word in full_name.split():
            full_name = full_name.replace(word, word.capitalize())
        registration_email = registration_email.strip()
        try:
            validate_email(registration_email)
        except Exception:
            return handle_400_error('Email inválido!')
        staff.full_name = full_name
        staff.is_manager = is_manager
        staff.save()
        return response.Response(status=status.HTTP_201_CREATED, data='Monitor adicionado com sucesso!')


class DeleteAllStaffs(BaseView):
    permission_classes = [IsAuthenticated, StaffPermissions]

    @ swagger_auto_schema(
        tags=['staff'],
        operation_description="""Deleta todos os monitores associados ao evento. Apenas o Admin do evento pode realizar essa ação.""",
        operation_summary='Deleta todos os monitores associados ao evento.',
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(
            'Monitores deletados com sucesso!'), **Errors([400]).retrieve_erros()}
    )
    def delete(self, request: request.Request, *args, **kwargs):
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        staffs = Staff.objects.filter(event=event)
        staffs.delete()
        return response.Response(status=status.HTTP_200_OK, data='Monitores deletados com sucesso!')
