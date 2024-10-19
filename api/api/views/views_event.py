from typing import Optional
from django.contrib.auth.models import Group

from django.forms import ValidationError
from rest_framework import status, request, response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission

from ..views.base_views import BaseView
from api.models import Token, Event, Staff, Player, Results
from ..serializers import EventSerializer, PlayerResultsSerializer, UserEventsSerializer, ResultsSerializer
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
            'OK'), **Errors([400]).retrieve_erros()}
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
            token.mark_as_used()
            event.name = name

        response_status, data = self.handle_event_permissions(
            request, event, created)
        if response_status != status.HTTP_201_CREATED:
            return response.Response(status=response_status, data=data)

        self.assign_event_admin_permissions(request, event)
        Results.objects.create(event=event)
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
            event = self.get_event()
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


class ResultsPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'PUT':
            return request.user.has_perm('api.change_event', obj)
        if request.method == 'DELETE':
            return request.user.has_perm('api.delete_event', obj)
        if request.method == 'GET':
            return request.user.has_perm('api.view_player_event', obj)
        return True


class ResultsView(BaseView):
    permission_classes = [IsAuthenticated, ResultsPermissions]

    @swagger_auto_schema(
        operation_description="""
        Publica TODOS os resultados do evento. Apenas o admin pode realizar a publicacao.
        Os jogadores poderão ver suas próprias pontuações, além de verem o paladino, o embaixador, os top4 finalistas e os imortais.

        Deve ser enviado ao menos um dos campos a seguir:  **top4** jogadores,**paladino** e **embaixador**.
        Os jogadores devem ser enviados como uma lista de dicionários com os campos *player* e *total_score*.
        Os top3 imortais serão calculados automaticamente, não é necessário enviar.
        """,
        tags=['results'],
        operation_summary="Publica os resultados finais do evento",
        manual_parameters=manual_parameter_event_id,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'top4': openapi.Schema(type=openapi.TYPE_ARRAY, description='Lista dos top4 jogadores do RRDD', items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                    'player_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador'),
                })),
                'paladin': openapi.Schema(
                    type=openapi.TYPE_OBJECT, description='Jogador que foi o paladino',
                    properties={'player_id': openapi.Schema(
                        type=openapi.TYPE_INTEGER, description='ID do jogador')}),
                'ambassor': openapi.Schema(
                    type=openapi.TYPE_OBJECT, description='Jogador que foi o embaixador',
                    properties={'player_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador')})
            },
        ),
        responses={200: openapi.Response(
            'OK', ResultsSerializer), **Errors([400]).retrieve_erros()}
    )
    def put(self, request: request.Request, *args, **kwargs):
        required_fields = ['top4', 'paladin', 'ambassor']
        if not any(field in request.data for field in required_fields):
            return handle_400_error(
                'Nenhum campo fornecido: top4, paladin, ambassor.')
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        if event not in request.user.events.all():
            return response.Response(status=status.HTTP_403_FORBIDDEN, data={'errors': 'Você não tem permissão para acessar este evento.'})
        self.check_object_permissions(request, event)
        results = Results.objects.get(event=event)
        if 'top4' in request.data:
            if not isinstance(request.data['top4'], list):
                return handle_400_error('top4 deve ser uma lista.')
            top4_requset = request.data['top4']
            for player in top4_requset:
                if 'player_id' not in player:
                    continue
                player = Player.objects.filter(
                    id=player['player_id'], event=event).first()
                if player:
                    results.top4.add(player)
        if 'paladin' in request.data:
            paladin_request = request.data['paladin']
            paladin = Player.objects.filter(
                id=paladin_request['player_id'], event=event).first() if 'player_id' in paladin_request else None
            if paladin:
                results.paladin = paladin
        if 'ambassor' in request.data:
            ambassor_request = request.data['ambassor']
            ambassor = Player.objects.filter(id=ambassor_request['player_id'], event=event).first(
            ) if 'player_id' in ambassor_request else None
            if ambassor:
                results.ambassor = ambassor
        results.save()
        event.is_final_results_published = True
        # event.is_imortal_results_published = True
        event.save()
        return response.Response(status=status.HTTP_200_OK, data='Resultados atribuídos e publicados com sucesso!')

    @swagger_auto_schema(
        operation_description="""Deleta os resultados de um evento e revoga a publicação dos resultados.
        Os campos top4, paladin e ambassor serão limpos, mas o cálculo dos imortais não será afetado, porém a publicação dos resultados imortal será revogada.
        """,
        operation_summary="Deleta os resultados de um evento.",
        tags=['results'],
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(
            'OK'), **Errors([400]).retrieve_erros()})
    def delete(self, request: request.Request, *args, **kwargs):
        """Deleta o resultado de um evento."""
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        if event not in request.user.events.all():
            return response.Response(status=status.HTTP_403_FORBIDDEN, data={'errors': 'Você não tem permissão para acessar este evento.'})
        results = Results.objects.get(event=event)
        results.top4.clear()
        results.paladin = None
        results.ambassor = None
        results.imortals.clear()
        results.save()
        event.is_final_results_published = False
        event.is_imortal_results_published = False
        event.save()
        return response.Response(status=status.HTTP_200_OK, data='Resultados deletados com sucesso.')

    @swagger_auto_schema(
        tags=['results'],
        operation_summary="Retorna os resultados de um evento.",
        operation_description="""Retorna os resultados de um evento.
        Os resultados são compostos por top4, imortais, paladino e embaixador.

        Valor de retorno:
        - **id**: ID do objeto results.
        - **top4**: Lista dos top4 jogadores do RRDD. **Caso os resultados **
        """,
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(
            'OK', openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do objeto results', example=5),
                'top4': openapi.Schema(
                    type=openapi.TYPE_ARRAY, description='Lista dos top4 jogadores do RRDD',
                    items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador', example=5),
                        'total_score': openapi.Schema(type=openapi.TYPE_INTEGER, description='Pontuação total do jogador', example=98),
                        'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome completo do jogador', example='João da Silva'),
                        'social_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome social do jogador', example='João'),
                    })),
                'paladin': openapi.Schema(
                    type=openapi.TYPE_OBJECT, description='Jogador que foi o paladino',
                    properties={'id': openapi.Schema(
                        type=openapi.TYPE_INTEGER, description='ID do jogador'),
                        'total_score': openapi.Schema(type=openapi.TYPE_INTEGER, description='Pontuação total do jogador', example=98),
                        'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome completo do jogador', example='João da Silva'),
                        'social_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome social do jogador', example='João'), }),
                'ambassor': openapi.Schema(
                    type=openapi.TYPE_OBJECT, description='Jogador que foi o embaixador',
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador'),
                        'total_score': openapi.Schema(type=openapi.TYPE_INTEGER, description='Pontuação total do jogador', example=98),
                        'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome completo do jogador', example='João da Silva'),
                        'social_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome social do jogador', example='João'), }),
                'imortals': openapi.Schema(
                   type=openapi.TYPE_ARRAY, description='Lista dos top3 imortais do RRDD',
                    items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador', example=5),
                        'total_score': openapi.Schema(type=openapi.TYPE_INTEGER, description='Pontuação total do jogador', example=98),
                        'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome completo do jogador', example='João da Silva'),
                        'social_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome social do jogador', example='João'),
                    })),

            }

            ),
        ), **Errors([400]).retrieve_erros()}
    )
    def get(self, request: request.Request, *args, **kwargs):
        try:
            event = self.get_event()
        except Exception as e:
            return handle_400_error(str(e))
        if event not in request.user.events.all():
            return response.Response(status=status.HTTP_403_FORBIDDEN, data={'errors': 'Você não tem permissão para acessar este evento.'})
        if not event.is_final_results_published and not event.is_imortal_results_published:
            return handle_400_error('Resultados ainda não publicados.')
        results = Results.objects.get(event=event)
        if event.is_imortal_results_published:
            results.calculate_imortals()
        data = ResultsSerializer(results).data
        return response.Response(status=status.HTTP_200_OK, data=data)


class PublishFinalResults(BaseView):
    permission_classes = [IsAuthenticated, ResultsPermissions]

    # @ swagger_auto_schema(
    #     tags=['results'],
    #     security=[{'Bearer': []}],
    #     operation_description="""Publica TODOS os resultados do evento. Apenas o admin pode realizar a publicacao.
    #     Os jogadores poderão ver suas próprias pontuações, além de verem o paladino, o embaixador, os top4 finalistas e os imortais.""",
    #     operation_summary="""Publica os resultados finais do evento.""",
    #     manual_parameters=manual_parameter_event_id,
    #     responses={200: openapi.Response(
    #         200), **Errors([400]).retrieve_erros()}
    # )
    # def put(self, request: request.Request, *args, **kwargs) -> response.Response:
    #     try:
    #         event = self.get_event()
    #     except ValidationError as e:
    #         return handle_400_error(str(e))
    #     self.check_object_permissions(request, event)
    #     event.is_final_results_published = True
    #     event.is_imortal_results_published = True
    #     event.save()
    #     return response.Response(status=status.HTTP_200_OK, data='Resultados publicados com sucesso!')


class PublishImortalsResults(BaseView):
    permission_classes = [IsAuthenticated, ResultsPermissions]

    @ swagger_auto_schema(
        tags=['results'],
        security=[{'Bearer': []}],
        operation_description="""Publica os resultados **APENAS** dos **top3 imortais** do evento. Apenas o admin pode realizar a publicacao.
        **Os jogadores poderão ver APENAS suas próprias pontuações e os imortais.**""",
        operation_summary="""Publica os resultados dos top3 imortais do evento.""",
        manual_parameters=manual_parameter_event_id,
        responses={200: openapi.Response(
            200), **Errors([400]).retrieve_erros()}
    )
    def put(self, request: request.Request, *args, **kwargs) -> response.Response:
        try:
            event = self.get_event()
        except ValidationError as e:
            return handle_400_error(str(e))
        self.check_object_permissions(request, event)
        event.is_imortal_results_published = True
        event.save()
        return response.Response(status=status.HTTP_200_OK, data='Resultados de imortais publicados com sucesso!')


# class Top3ImortalPlayers(BaseView):
#     permission_classes = [IsAuthenticated, ResultsPermissions]

#     @ swagger_auto_schema(
#         tags=['results'],
#         security=[{'Bearer': []}],
#         operation_description='Retorna os 3 jogadores com mais pontos do evento.',
#         operation_summary='Retorna os 3 primeiros jogadores do evento.',
#         manual_parameters=manual_parameter_event_id,
#         responses={200: openapi.Response(200, PlayerResultsSerializer), **Errors([400]).retrieve_erros()})
#     def get(self, request: request.Request, *args, **kwargs) -> response.Response:
#         try:
#             event = self.get_event()
#         except ValidationError as e:
#             return handle_400_error(str(e))
#         self.check_object_permissions(request, event)
#         if not event.is_imortal_results_published:
#             return response.Response(status=status.HTTP_403_FORBIDDEN, data='Resultados não publicados!')
#         results = Results.objects.get(event=event)
#         results.calculate_imortals()
#         players = [player for player in results.imortals.all()]
#         data = PlayerResultsSerializer(players, many=True).data
#         return response.Response(status=status.HTTP_200_OK, data=data)
