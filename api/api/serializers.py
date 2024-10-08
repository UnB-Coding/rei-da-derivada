from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from api.models import SumulaClassificatoria, Token, Event, Sumula, PlayerScore, Player, Staff, SumulaImortal, Results
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
        fields = ['id', 'full_name', 'social_name', 'is_imortal', 'is_present']


class PlayerForRoundRobinSerializer(ModelSerializer):
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
        fields = ['id', 'points', 'rounds_number', 'player']


class PlayerScoreForRoundRobinSerializer(ModelSerializer):
    player = PlayerForRoundRobinSerializer()

    class Meta:
        model = PlayerScore
        fields = ['id', 'rounds_number', 'player']


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
                  'description', 'referee',  'players_score', 'rounds']


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
                  'description', 'referee',  'players_score', 'rounds']


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
        fields = ['id', 'active', 'name', 'description',
                  'referee', 'players', 'rounds']


class SumulaImortalForPlayerSerializer(ModelSerializer):
    """ Serializer for the Sumula model.
    fields: id, active, referee, name, players_score
    """
    referee = StaffSerializer(many=True)
    players = PlayerScoreForPlayerSerializer(source='scores', many=True)

    class Meta:
        model = SumulaImortal
        fields = ['id', 'active', 'name', 'description',
                  'referee', 'players', 'rounds']


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
        fields = ['id', 'full_name', 'social_name',
                  'is_imortal', 'is_present', 'event']


class ResultsSerializer(ModelSerializer):
    top4 = serializers.SerializerMethodField()
    imortals = serializers.SerializerMethodField()
    ambassor = serializers.SerializerMethodField()
    paladin = serializers.SerializerMethodField()

    class Meta:
        model = Results
        fields = ['id', 'top4', 'imortals', 'ambassor', 'paladin']

    def get_top4(self, obj):
        if not obj.event.is_final_results_published:
            return None
        result = PlayerResultsSerializer(obj.top4, many=True).data
        if len(result) == 0:
            return None
        return result

    def get_imortals(self, obj):
        result = PlayerResultsSerializer(obj.imortals, many=True).data
        if len(result) == 0:
            return None
        return result

    def get_ambassor(self, obj):
        if not obj.event.is_final_results_published:
            return None
        result = PlayerResultsSerializer(obj.ambassor).data
        return result
    def get_paladin(self, obj):
        if not obj.event.is_final_results_published:
            return None
        result = PlayerResultsSerializer(obj.paladin).data
        return result
