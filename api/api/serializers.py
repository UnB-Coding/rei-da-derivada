from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from api.models import Token, Event, Sumula, PlayerScore, Player, Staff
from users.models import User


class UserSerializer(ModelSerializer):
    """ Serializer for the User model.
    fields: first_name, last_name, id
    """
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class PlayerSerializer(ModelSerializer):
    """ Serializer for the Player model.
    fields: full_name, social_name event, total_score, registration_email, id
    """
    user = UserSerializer()

    class Meta:
        model = Player
        fields = ['id', 'total_score', 'full_name', 'social_name', 'user']


class PlayerResultsSerializer(ModelSerializer):
    """ Serializer for the Player model. Returns only the necessary fields for results.
    fields: 'id', 'total_score', 'full_name', 'social_name'
    """
    class Meta:
        model = Player
        fields = ['id', 'total_score', 'full_name', 'social_name']


class PlayerWithoutScoreSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'full_name', 'social_name']


class TokenSerializer(ModelSerializer):
    class Meta:
        model = Token
        fields = ['token_code']


class EventSerializer(ModelSerializer):
    """ Serializer for the Event model.
    fields: 'id', 'name','active'
    """
    class Meta:
        model = Event
        fields = ['id', 'name', 'active']


# class PlayerScoreSerializer(ModelSerializer):
#     player = PlayerSerializer()

#     class Meta:
#         model = PlayerScore
#         fields = ['id', 'player', 'sumula', 'points']


class PlayerScoreSerializer(ModelSerializer):
    player = PlayerWithoutScoreSerializer()

    class Meta:
        model = PlayerScore
        fields = ['id', 'points', 'player']


class SumulaSerializer(ModelSerializer):
    """ Serializer for the Sumula model.
    fields: id, active, description, referee, name, players_score
    """
    players_score = PlayerScoreSerializer(
        source='scores', many=True)
    referee = UserSerializer(many=True)

    class Meta:
        model = Sumula
        fields = ['id', 'active', 'name',
                  'description', 'referee',  'players_score']


class StaffSerializer(ModelSerializer):
    """ Serializer for the Staff model.
    fields: id, full_name, event, registration_email
    """
    user = UserSerializer()

    class Meta:
        model = Staff
        fields = ['id', 'full_name', 'registration_email', 'user']


class UploadFileSerializer(serializers.Serializer):
    file = serializers.FileField()


class PlayerScoreForPlayerSerializer(ModelSerializer):
    player = PlayerResultsSerializer()

    class Meta:
        model = PlayerScore
        fields = ['player']


class SumulaForPlayerSerializer(ModelSerializer):
    """ Serializer for the Sumula model.
    fields: id, active, referee, name, players_score
    """
    referee = UserSerializer(many=True)
    players = PlayerScoreForPlayerSerializer(source='scores', many=True)

    class Meta:
        model = Sumula
        fields = ['id', 'active', 'name', 'description', 'referee', 'players']
