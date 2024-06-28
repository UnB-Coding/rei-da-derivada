from django.contrib.auth.models import Group
from rest_framework import status, request, response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from .base_views import BaseSumulaView, SUMULA_NOT_FOUND_ERROR_MESSAGE, SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE
from api.models import Staff, SumulaClassificatoria, SumulaImortal, PlayerScore, Player
from ..serializers import SumulaSerializer, SumulaForPlayerSerializer, SumulaImortalSerializer, SumulaClassificatoriaSerializer, SumulaClassificatoriaForPlayerSerializer, SumulaImortalForPlayerSerializer
from rest_framework.permissions import BasePermission
from ..utils import handle_400_error
from ..swagger import Errors, sumula_imortal_api_put_schema, sumula_classicatoria_api_put_schema, sumulas_response_schema
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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


class GetSumulasView(BaseSumulaView):
    """Lida com os requests relacionados a sumulas."""
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @ swagger_auto_schema(
        operation_summary="Retorna todas as sumulas associadas a um evento.",
        operation_description="Retorna todas as sumulas associadas a um evento com seus jogadores e pontuações.",
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, description="Id do evento associado às sumulas.", type=openapi.TYPE_INTEGER, required=True)],
        responses={200: openapi.Response('OK', sumulas_response_schema), **Errors([400]).retrieve_erros()})
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Retorna todas as sumulas associadas a um evento."""
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        sumulas_imortal, sumulas_classificatoria = self.get_sumulas(
            event=event)
        data = SumulaSerializer(
            {'sumula_classificatoria': sumulas_classificatoria, 'sumula_imortal': sumulas_imortal}).data
        return response.Response(status=status.HTTP_200_OK, data=data)


class SumulaClassificatoriaView(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @swagger_auto_schema(
        operation_summary="Cria uma nova sumula classificatoria.",
        operation_description="Cria uma nova sumula classificatoria e retorna a sumula criada com os jogadores e suas pontuações.",
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.", type=openapi.TYPE_INTEGER, required=True)],
        request_body=openapi.Schema(
            title='Sumula',
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome da sumula'),
                'players': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    title='Players',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador'),
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do jogador'),
                        }
                    ),
                    description='Lista de jogadores',
                ),
                'referees': openapi.Schema(
                    type=openapi.TYPE_ARRAY, title='Staffs',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do Staff')}),
                    description='Lista de objetos Staff'),
            },
            required=['name', 'players'],
        ),
        responses={201: openapi.Response(
            'Created', SumulaClassificatoriaSerializer), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Cria uma nova sumula classificatoria e retorna a sumula criada.

        Permissões necessárias: IsAuthenticated, HasSumulaPermission
        """
        if not self.validate_request_data(request.data):
            return handle_400_error("Dados inválidos!")
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        if 'name' not in request.data:
            return handle_400_error("Nome da sumula não fornecido!")
        if not self.validate_players(request.data):
            return handle_400_error("Dados de players inválidos!")

        self.check_object_permissions(self.request, event)
        name = request.data['name']
        players = request.data['players']
        sumula = SumulaClassificatoria.objects.create(event=event, name=name)
        try:
            self.create_players_score(
                players=players, sumula=sumula, event=event)
        except Exception as e:
            return handle_400_error(str(e))
        data = SumulaClassificatoriaSerializer(sumula).data
        return response.Response(status=status.HTTP_201_CREATED, data=data)

    @ swagger_auto_schema(
        operation_summary="Atualiza uma sumula.",
        operation_description="""Atualiza os dados associados a uma sumula criada.
                         """,
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter('event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.",
                                             type=openapi.TYPE_INTEGER, required=True)],
        request_body=sumula_classicatoria_api_put_schema,
        responses={200: openapi.Response('OK'), **Errors([400]).retrieve_erros()})
    def put(self, request: request.Request, *args, **kwargs):
        """Atualiza uma sumula de Classificatoria"""
        if not request.data or not isinstance(request.data, list) or 'id' not in request.data[0]:
            return handle_400_error("Dados inválidos!")

        sumula_id = request.data[0]['id']
        if not sumula_id:
            return handle_400_error(SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE)
        sumula = SumulaClassificatoria.objects.filter(id=sumula_id).first()
        if not sumula:
            return handle_400_error(SUMULA_NOT_FOUND_ERROR_MESSAGE)
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))

        # Verifica se o usuário tem permissão para acessar o evento
        self.check_object_permissions(request, event)
        if 'name' not in request.data[0] or 'description' not in request.data[0] or 'referee' not in request.data[0]:
            return handle_400_error("Dados inválidos!")
        sumula.name = request.data[0]['name']
        sumula.description = request.data[0]['description']
        # referees = request.data[0]['referee']
        # self.add_referee(sumula, referees) necessario refatorar com outra rota apenas para atribuir referee.
        ########## FALTA IMPLEMENTAR: lógica de tornar os players não classificados como imortal ##########
        players_score = request.data[0]['players_score']

        if not self.update_player_score(players_score):
            return handle_400_error("Dados de pontuação inválidos!")

        sumula.active = False
        sumula.save()
        return response.Response(status=status.HTTP_200_OK)


class SumulaImortalView(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @ swagger_auto_schema(
        operation_summary="Cria uma nova sumula imortal.",
        operation_description="Cria uma nova sumula imortal e retorna a sumula criada com os jogadores e suas pontuações.",
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter(
            'event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.", type=openapi.TYPE_INTEGER, required=True)],
        request_body=openapi.Schema(
            title='Sumula',
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome da sumula'),
                'players': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    title='Players',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador'),
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do jogador'),
                        }
                    ),
                    description='Lista de jogadores',
                ),
                'referees': openapi.Schema(
                    type=openapi.TYPE_ARRAY, title='Staffs',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do Staff')}),
                    description='Lista de objetos Staff'),
            },
            required=['name', 'players'],
        ),
        responses={201: openapi.Response(
            'Created', SumulaImortalSerializer), **Errors([400]).retrieve_erros()}
    )
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Cria uma nova sumula imortal e retorna a sumula criada.

        Permissões necessárias: IsAuthenticated, HasSumulaPermission
        """
        if not self.validate_request_data(request.data):
            return handle_400_error("Dados inválidos!")
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        if 'name' not in request.data:
            return handle_400_error("Nome da sumula não fornecido!")
        if not self.validate_players(request.data):
            return handle_400_error("Dados de players inválidos!")
        self.check_object_permissions(self.request, event)

        players = request.data['players']
        name = request.data['name']
        sumula = SumulaImortal.objects.create(
            event=event, name=name)
        try:
            self.create_players_score(
                players=players, sumula=sumula, event=event)
        except Exception as e:
            return handle_400_error(str(e))
        referees = request.data['referees']
        self.add_referees(sumula=sumula, event=event, referees=referees)
        data = SumulaImortalSerializer(sumula).data
        return response.Response(status=status.HTTP_201_CREATED, data=data)

    @ swagger_auto_schema(
        operation_summary="Atualiza uma sumula Imortal.",
        operation_description="""Atualiza uma sumula
        Obtém o id da sumula a ser atualizada e atualiza os dados associados a ela.
        Obtém uma lista da pontuação dos jogadores e atualiza as pontuações associados a sumula.
        Marca a sumula como encerrada """,
        security=[{'Bearer': []}],
        manual_parameters=[openapi.Parameter('event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.",
                                             type=openapi.TYPE_INTEGER, required=True)],
        request_body=sumula_imortal_api_put_schema,
        responses={200: openapi.Response('OK'), **Errors([400]).retrieve_erros()})
    def put(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Atualiza uma sumula
        Obtém o id da sumula a ser atualizada e atualiza os dados associados a ela.
        Obtém uma lista da pontuação dos jogadores e atualiza as pontuações associados a sumula.
        Marca a sumula como encerrada.
        """

        if not request.data or not isinstance(request.data, list) or 'id' not in request.data[0]:
            return handle_400_error("Dados inválidos!")

        sumula_id = request.data[0]['id']
        if not sumula_id:
            return handle_400_error(SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE)
        sumula = SumulaImortal.objects.filter(id=sumula_id).first()
        if not sumula:
            return handle_400_error(SUMULA_NOT_FOUND_ERROR_MESSAGE)
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))

        # Verifica se o usuário tem permissão para acessar o evento
        self.check_object_permissions(request, event)
        if 'name' not in request.data[0] or 'description' not in request.data[0] or 'referee' not in request.data[0]:
            return handle_400_error("Dados inválidos!")
        sumula.name = request.data[0]['name']
        sumula.description = request.data[0]['description']
        # referees = request.data[0]['referee']
        # self.add_referee(sumula, referees) necessario refatorar com outra rota apenas para atribuir referee.

        players_score = request.data[0]['players_score']

        if not self.update_player_score(players_score):
            return handle_400_error("Dados de pontuação inválidos!")

        sumula.active = False
        sumula.save()
        return response.Response(status=status.HTTP_200_OK)


class ActiveSumulaView(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @ swagger_auto_schema(
        operation_summary="Retorna todas as sumulas ativas associadas a um evento.",
        operation_description="Retorna todas as sumulas ativas associadas a um evento, com seus jogadores e pontuações.",
        manual_parameters=[openapi.Parameter(
                              'event_id', openapi.IN_QUERY, description="Id do evento associado às sumulas.", type=openapi.TYPE_INTEGER, required=True)],
        responses={200: openapi.Response(
            'OK', sumulas_response_schema), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request):
        """Retorna todas as sumulas ativas."""
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        sumula_imortal, sumula_classificatoria = self.get_sumulas(
            event=event, active=True)
        data = SumulaSerializer(
            {'sumula_classificatoria': sumula_classificatoria, 'sumula_imortal': sumula_imortal}).data
        return response.Response(status=status.HTTP_200_OK, data=data)


class FinishedSumulaView(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @ swagger_auto_schema(
        operation_summary="Retorna todas as sumulas encerradas associadas a um evento.",
        operation_description="Retorna todas as sumulas encerradas associadas a um evento, com seus jogadores e pontuações.",
        manual_parameters=[openapi.Parameter(
                              'event_id', openapi.IN_QUERY, description="Id do evento associado às sumulas.", type=openapi.TYPE_INTEGER, required=True)],
        responses={200: openapi.Response(
            'OK', sumulas_response_schema), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request):
        """Retorna todas as sumulas encerradas."""
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        sumula_imortal, sumula_classificatoria = self.get_sumulas(
            event=event, active=False)
        data = SumulaSerializer(
            {'sumula_classificatoria': sumula_classificatoria, 'sumula_imortal': sumula_imortal}).data
        return response.Response(status=status.HTTP_200_OK, data=data)


class GetSumulaForPlayerPermission(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if Group.objects.get(name='app_admin') in request.user.groups.all():
            return True
        if request.method == 'GET':
            return request.user.has_perm('api.view_event', obj)
        return False


class GetSumulaForPlayer(BaseSumulaView):
    permission_classes = [IsAuthenticated, GetSumulaForPlayerPermission]

    @ swagger_auto_schema(
        operation_summary="Retorna as sumulas ativas para um jogador.",
        operation_description="""
        Retorna todas as sumulas ativas para o jogador. São omitidos pontuações da sumula.""",
        manual_parameters=[openapi.Parameter(
                              'event_id', openapi.IN_QUERY, description="Id do evento associado às sumulas.", type=openapi.TYPE_INTEGER, required=True)],
        responses={200: openapi.Response(
            'OK', SumulaForPlayerSerializer), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        """Retorna todas as sumulas ativas associadas a um jogador."""
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)

        player = Player.objects.filter(user=request.user, event=event).first()
        if not player:
            return handle_400_error("Jogador não encontrado!")

        if player.is_imortal:
            player_scores = PlayerScore.objects.filter(
                player=player, sumula_imortal__active=True)
            if not player_scores:
                return handle_400_error("Jogador não possui nenhuma sumula associada!")
            sumulas = [
                player_score.sumula_imortal for player_score in player_scores]
            data = SumulaImortalForPlayerSerializer(
                sumulas, many=True).data
        else:
            player_scores = PlayerScore.objects.filter(
                player=player, sumula_classificatoria__active=True)
            if not player_scores:
                return handle_400_error("Jogador não possui nenhuma sumula associada!")
            sumulas = [
                player_score.sumula_classificatoria for player_score in player_scores]
            data = SumulaClassificatoriaForPlayerSerializer(
                sumulas, many=True).data

        return response.Response(status=status.HTTP_200_OK, data=data)


class AddRefereeToSumulaView(BaseSumulaView):
    permission_classes = [IsAuthenticated, HasSumulaPermission]

    @swagger_auto_schema(
        operation_description="""
        Adiciona um árbitro a uma súmula que já existe.
        Caso uma súmula seja criada sem nenhum árbitro, é possível que um usuário monitor se auto adicione como árbitro ao selecionar a sumula desejada.
        Apenas o usuário que fez a requisição será adicionado como árbitro da súmula.
        Esta rota verifica se o usuário em questão tem as permissões necessárias para ser um árbitro no evenot e se possui um objeto staff associado a ele.

            É necessário fornecer o id da súmula e indicar se a súmula é imortal ou classificatória no corpo da requisição.
        """,
        operation_summary="Adiciona um árbitro a uma súmula.",
        request_body=openapi.Schema(
            title='Sumula',
            type=openapi.TYPE_OBJECT,
            properties={
                'sumula_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Id da sumula imortal'),
                'is_imortal': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indica se a sumula é imortal ou classificatória', example=True)
            },
            required=['sumula_id', 'is_imortal'],
        ),
        manual_parameters=[
            openapi.Parameter('event_id', openapi.IN_QUERY, description="Id do evento associado a sumula.",
                              type=openapi.TYPE_INTEGER, required=True)],
        responses={200: openapi.Response('OK'), **Errors([400]).retrieve_erros()})
    def put(self, request: request.Request, *args, **kwargs):
        if not self.validate_request_data(request.data):
            return handle_400_error("Dados inválidos!")
        try:
            event = self.get_object()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(self.request, event)
        staff = Staff.objects.filter(user=request.user, event=event).first()
        if not staff:
            return handle_400_error("Usuário não é um monitor do evento!")
        if 'sumula_id' not in request.data or 'is_imortal' not in request.data:
            return handle_400_error(SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE)
        sumula_id = request.data.get('sumula_id')
        if not sumula_id:
            return handle_400_error(SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE)
        is_imortal = request.data.get('is_imortal')
        if is_imortal:
            sumula = SumulaImortal.objects.filter(id=sumula_id).first()
        else:
            sumula = SumulaClassificatoria.objects.filter(id=sumula_id).first()
        if not sumula:
            return handle_400_error(SUMULA_NOT_FOUND_ERROR_MESSAGE)
        sumula.referee.add(staff)
        return response.Response(status=status.HTTP_200_OK)
