from io import StringIO
from typing import Optional
from django.forms import ValidationError
from rest_framework import status, request, response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FileUploadParser, MultiPartParser
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import Event, Player
from users.models import User
from ..serializers import PlayerSerializer, PlayerScoreSerializer, SumulaSerializer, UserSerializer
from rest_framework.permissions import BasePermission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ..utils import handle_400_error
from ..swagger import Errors
import pandas as pd


class PlayersPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return request.user.has_perm('api.view_player_event', obj)
        if request.method == 'POST':
            return request.user.has_perm('api.add_player_event', obj)
        if request.method == 'PUT':
            return request.user.has_perm('api.change_player_event', obj)
        if request.method == 'DELETE':
            return request.user.has_perm('api.delete_player_event', obj)
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
        """ Retorna todos os jogadores de um evento."""
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)

        players = Player.objects.filter(event=event)
        if not players:
            return response.Response(status=status.HTTP_200_OK, data=['Nenhum jogador encontrado!'])
        players_list = []
        for player in players:
            players_list.append(player)

        data = PlayerSerializer(players_list, many=True).data

        return response.Response(status=status.HTTP_200_OK, data=data)

    def get_object(self) -> Event:
        if 'event_id' not in self.request.query_params:
            raise ValidationError('Dados inválidos!')

        event_id = self.request.query_params.get('event_id')
        if not event_id:
            raise ValidationError('event_id é obrigatório!')
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise ValidationError('Evento não encontrado!')
        return event


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
        """ Retorna as informações do jogador atual do usuário logado."""
        try:
            event = self.get_object()
        except ValidationError as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        player = Player.objects.filter(event=event, user=request.user).first()
        if not player:
            return handle_400_error('Jogador não encontrado!')

        data = PlayerSerializer(player).data

        return response.Response(status=status.HTTP_200_OK, data=data)

    def get_object(self) -> Event:
        if 'event_id' not in self.request.query_params:
            raise ValidationError('Dados inválidos!')

        event_id = self.request.query_params.get('event_id')
        if not event_id:
            raise ValidationError('event_id é obrigatório!')
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise ValidationError('Evento não encontrado!')
        return event


class AddPlayers(APIView):
    # permission_classes = [IsAuthenticated, PlayersPermission]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description='Adiciona os jogadores ao evento através do excel fornecido pelo administrador com os participantes do evento.',
        operation_summary='Adiciona multiplos jogadores ao evento.',
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Id do evento')],
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'file': openapi.Schema(
            type=openapi.TYPE_FILE, description='Arquivo com os jogadores. Formatos aceitos: .csv,.xlsx e .xls')}, required=['file']),
        responses={201: openapi.Response(
            201), **Errors([400]).retrieve_erros()})
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Adiciona os jogadores ao evento através do excel
        forncecido pelo administrador com os participantes do evento."""
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
        self.create_players(df=df, event=event)
        return response.Response(status=status.HTTP_201_CREATED, data='Jogadores adicionados com sucesso!')

    def create_players(self, df: pd.DataFrame, event: Event) -> None:
        process_data = ['Nome Completo', 'E-mail']
        df_needed = df[process_data]

        for i, line in df_needed.iterrows():
            name = line['Nome Completo']
            email = line['E-mail']
            player, created = Player.objects.get_or_create(
                full_name=name, registration_email=email, event=event)
            if created:
                player.full_name = name
                player.registration_email = email
                player.event = event
                player.save()

    def createData(self, extension, file) -> Optional[pd.DataFrame]:
        data = None
        if extension == 'csv':
            # Lê os dados do arquivo como uma string
            file_data = file.read().decode('utf-8')
            # Converte a string em um StringIO, que pode ser lido pelo pandas
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
