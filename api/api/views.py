from requests import Response
from rest_framework import response, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.models import Token, Event
from .serializers import TokenSerializer, EventSerializer
from django.contrib.auth.mixins import PermissionRequiredMixin
from rest_framework.permissions import BasePermission
from django.contrib.auth.decorators import permission_required
from .utils import handle_400_error

TOKEN_NOT_PROVIDED_ERROR_MESSAGE = "Token não fornecido!"
TOKEN_ERROR_MESSAGE = "Token não encontrado!"
EVENT_CREATE_ERROR_MESSAGE = "Evento não encontrado!"
EVENT_DELETE_ERROR_MESSAGE = "Este evento não existe!"


class TokenView(APIView):
    """ TokenView é uma view que lida com os requests relacionados a tokens."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Cria um novo token e retorna o código do token gerado."""
        if not request.user.has_perm('api.add_token'):
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        token = Token.objects.create()
        data = TokenSerializer(token).data
        return response.Response(status=status.HTTP_200_OK, data=data)


class CanAddEvent(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.has_perm('api.add_event')
        return True


class CanDeleteEvent(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return request.user.has_perm('api.delete_event')
        return True


class EventView(APIView):
    """Lida com os requests relacionados a eventos."""
    permission_classes = [IsAuthenticated, CanAddEvent, CanDeleteEvent]

    def get_permission_required(self):
        if self.request.method == 'POST':
            return ['api.add_event']
        elif self.request.method == 'DELETE':
            return ['api.delete_event']
        else:
            return []

    def get_token(self, token_code: str) -> Token:
        """Retorna um token com o código fornecido."""
        return Token.objects.filter(
            token_code=token_code).first()

    def get_event(self, token: Token) -> Event:
        """Retorna um evento com o código fornecido."""
        return Event.objects.filter(
            token=token).first()

    def token_code_exists(self, token_code: str) -> bool:
        """Verifica se o código do token fornecido na requisição é válido."""
        if len(token_code) == 0 or token_code.isspace():
            return False
        return True

    def post(self, request):
        """Cria um novo evento associado a um token e retorna o evento criado.
        Caso o token já tenha sido utilizado ou já exista um evento associado ao token, retorna um erro 400.
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

        event = Event.objects.create(token=token, name=request.data['name'])
        data = EventSerializer(event).data

        return response.Response(status=status.HTTP_201_CREATED, data=data)

    def delete(self, request):
        """Deleta um evento associado a um token e retorna o evento deletado.
        Caso o token não tenha um evento associado, retorna um erro 400.
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
