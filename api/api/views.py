from django.shortcuts import render
from requests import delete
from rest_framework import response, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.models import Token, Event
from .serializers import TokenSerializer, EventSerializer

# Create your views here.


class Token(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Create a new token
        token = Token.objects.create()
        data = TokenSerializer(token).data
        return response.Response(status=status.HTTP_200_OK, data=data)

    """ def delete(self, request):
        # Delete a token
        token = Token.objects.get(token_code=request.data['token_code'])
        token.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT) """
