from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from api.models import Token, Event, Sumula, PlayerScore, PlayerTotalScore
from users.models import User


class UserSerializer(ModelSerializer):
    """ Serializer for the User model.
    fields: first_name, last_name, id
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'id']


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
    user_ = UserSerializer()

    class Meta:
        model = PlayerScore
        fields = ['user_', 'event', 'sumula', 'points']


class PlayerScoreSerializerForSumula(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = PlayerScore
        fields = ['user', 'points']


class SumulaSerializer(ModelSerializer):
    """ Serializer for the Sumula model.
    fields: id, name, players_score
    returns: players_score as a list of PlayerScoreSerializer
    """
    players_score = PlayerScoreSerializerForSumula(
        source='playerscore_set', many=True)

    class Meta:
        model = Sumula
        fields = ['id', 'name', 'players_score']
