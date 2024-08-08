from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from api.models import SumulaClassificatoria, Token, Event, Sumula, PlayerScore, Player, Staff, SumulaImortal
from users.models import User


class UserSerializer(ModelSerializer):
    """ Serializer for the User model.
    fields: first_name, last_name, id
    """
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class PlayerResultsSerializer(ModelSerializer):
    """ Serializer for the Player model. Returns only the necessary fields for results.
    fields: 'id', 'total_score', 'full_name', 'social_name'
    """
    class Meta:
        model = Player
        fields = ['id', 'total_score', 'full_name', 'social_name']


class PlayerSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'full_name', 'social_name', 'is_imortal']


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


class UserEventsSerializer(serializers.Serializer):
    role = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()

    class Meta:
        fields = ['event', 'role']

    def get_role(self, obj):
        return obj["role"]

    def get_event(self, obj):
        return EventSerializer(obj['event']).data


class PlayerScoreSerializer(ModelSerializer):
    player = PlayerSerializer()

    class Meta:
        model = PlayerScore
        fields = ['id', 'points', 'player']


class StaffSerializer(ModelSerializer):
    """ Serializer for the Staff model.
    fields: id, full_name, event, registration_email
    """

    class Meta:
        model = Staff
        fields = ['id', 'full_name', 'registration_email', 'is_manager']


class SumulaClassificatoriaSerializer(ModelSerializer):
    """ Serializer for the SumulaClassificatoria model.
    fields: id, active, description, referee, name, players_score
    """
    players_score = PlayerScoreSerializer(
        source='scores', many=True)
    referee = StaffSerializer(many=True)

    class Meta:
        model = SumulaClassificatoria
        fields = ['id', 'active', 'name',
                  'description', 'referee',  'players_score']


class SumulaImortalSerializer(ModelSerializer):
    """ Serializer for the Sumula model.
    fields: id, active, description, referee, name, players_score
    """
    players_score = PlayerScoreSerializer(
        source='scores', many=True)
    referee = StaffSerializer(many=True)

    class Meta:
        model = SumulaImortal
        fields = ['id', 'active', 'name',
                  'description', 'referee',  'players_score']


class SumulaSerializer(serializers.Serializer):
    """ Serializer for the Sumula model.
    fields: id, active, description, referee, name, players_score
    """
    sumulas_classificatoria = serializers.SerializerMethodField()
    sumulas_imortal = serializers.SerializerMethodField()

    def get_sumulas_classificatoria(self, obj):
        return SumulaClassificatoriaSerializer(obj['sumulas_classificatoria'], many=True).data

    def get_sumulas_imortal(self, obj):
        return SumulaImortalSerializer(obj['sumulas_imortal'], many=True).data

    class Meta:
        fields = ['sumulas_classificatoria', 'sumulas_imortal']


class PlayerScoreForPlayerSerializer(ModelSerializer):
    player = PlayerSerializer()

    class Meta:
        model = PlayerScore
        fields = ['player']


class SumulaClassificatoriaForPlayerSerializer(ModelSerializer):
    """ Serializer for the Sumula model.
    fields: id, active, referee, name, players_score
    """
    referee = StaffSerializer(many=True)
    players = PlayerScoreForPlayerSerializer(source='scores', many=True)

    class Meta:
        model = SumulaClassificatoria
        fields = ['id', 'active', 'name', 'description', 'referee', 'players']


class SumulaImortalForPlayerSerializer(ModelSerializer):
    """ Serializer for the Sumula model.
    fields: id, active, referee, name, players_score
    """
    referee = StaffSerializer(many=True)
    players = PlayerScoreForPlayerSerializer(source='scores', many=True)

    class Meta:
        model = SumulaImortal
        fields = ['id', 'active', 'name', 'description', 'referee', 'players']


class SumulaForPlayerSerializer(serializers.Serializer):
    """ Serializer for the Sumula model.
    fields: id, active, description, referee, name, players_score
    """
    sumulas_classificatoria = serializers.SerializerMethodField()
    sumulas_imortal = serializers.SerializerMethodField()

    def get_sumulas_classificatoria(self, obj):
        return SumulaClassificatoriaForPlayerSerializer(obj['sumulas_classificatoria'], many=True).data

    def get_sumulas_imortal(self, obj):
        return SumulaImortalForPlayerSerializer(obj['sumulas_imortal'], many=True).data

    class Meta:
        fields = ['sumulas_classificatoria', 'sumulas_imortal']


class UploadFileSerializer(serializers.Serializer):
    file = serializers.FileField()


class StaffLoginSerializer(ModelSerializer):
    event = EventSerializer()

    class Meta:
        model = Staff
        fields = ['id', 'full_name', 'is_manager', 'event']


class PlayerLoginSerializer(ModelSerializer):
    event = EventSerializer()

    class Meta:
        model = Player
        fields = ['id', 'full_name', 'social_name', 'is_imortal', 'event']
