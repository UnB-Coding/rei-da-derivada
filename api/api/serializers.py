from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from api.models import Token, Event


class TokenSerializer(ModelSerializer):
    class Meta:
        model = Token
        fields = ['token_code']

class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ['name']
