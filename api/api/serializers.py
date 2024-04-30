from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from api.models import Token, Event, Sumula, PlayerScore, PlayerTotalScore
from users.models import User


class UserSerializer(ModelSerializer):
    """ Serializer for the User model.
    fields: first_name, last_name, uuid
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'uuid']


class TokenSerializer(ModelSerializer):
    class Meta:
        model = Token
        fields = ['token_code']


class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ['name', 'id']


class PlayerTotalScoreSerializer(ModelSerializer):
    class Meta:
        model = PlayerTotalScore
        fields = '__all__'


class PlayerScoreSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = PlayerScore
        fields = ['user', 'event', 'sumula', 'points']


class SumulaSerializer(ModelSerializer):
    players_score = PlayerScoreSerializer(source='playerscore_set', many=True)

    class Meta:
        model = Sumula
        fields = ['id', 'name', 'players_score']
