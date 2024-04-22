from curses import ERR
from django.shortcuts import render
from requests import delete
from rest_framework import response, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.models import Token, Event
from .serializers import TokenSerializer, EventSerializer
from .utils import handle_400_error
# Create your views here.
TOKEN_ERROR_MESSAGE = "Token não encontrado!"
EVENT_CREATE_ERROR_MESSAGE = "Evento não encontrado!"
EVENT_DELETE_ERROR_MESSAGE = "Este evento não existe!"


class TokenView(APIView):
    """ TokenView é uma view que lida com os requests relacionados a tokens."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Cria um novo token e retorna o código do token gerado."""
        token = Token.objects.create()
        data = TokenSerializer(token).data
        return response.Response(status=status.HTTP_200_OK, data=data)


class EventView(APIView):
    """Lida com os requests relacionados a eventos."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Cria um novo evento associado a um token e retorna o evento criado.
        Caso o token já tenha sido utilizado, retorna um erro 400.
        Caso já exista um evento associado ao token, retorna um erro 400.
        """
        token = Token.objects.get(token_code=request.data['token_code'])
        if not token:
            return handle_400_error(TOKEN_ERROR_MESSAGE)

        if Event.objects.filter(token=token).exists():
            return handle_400_error(EVENT_CREATE_ERROR_MESSAGE)

        event = Event.objects.create(token=token, name=request.data['name'])
        data = EventSerializer(event).data

        return response.Response(status=status.HTTP_200_OK, data=data)

    def delete(self, request):
        """Deleta um evento associado a um token e retorna o evento deletado.
        Caso o token não tenha um evento associado, retorna um erro 400.
        """
        token = Token.objects.get(token_code=request.data['token_code'])
        if not token:
            return handle_400_error(TOKEN_ERROR_MESSAGE)
        event = Event.objects.get(token=token)
        if not event:
            return handle_400_error(EVENT_DELETE_ERROR_MESSAGE)
        event.delete()
        return response.Response(status=status.HTTP_200_OK)
