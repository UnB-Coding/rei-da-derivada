from django.contrib import admin
from .models import Token, Event, Sumula, PlayerScore, Player, Staff
from guardian.admin import GuardedModelAdmin


@admin.register(Token)
class TokenAdmin(GuardedModelAdmin):
    def event(self, obj):
        return obj.event
    list_display = ['token_code', 'id', 'created_at', 'used', 'event']
    search_fields = ['token_code']
    fields = ['used']


@admin.register(Event)
class EventAdmin(GuardedModelAdmin):
    list_display = ['id', 'token', 'players_token', 'name', 'active']
    search_fields = ['token', 'name']
    fields = ['token', 'name', 'active']


@admin.register(Sumula)
class SumulaAdmin(GuardedModelAdmin):

    def referees(self, obj):
        referees = []
        for referee in obj.referee.all():
            referees.append(referee.__str__())
        return ', '.join(referees)

    def player_scores(self, obj):
        scores = []
        for score in obj.scores.all():
            scores.append(score.__str__())
        return ', '.join(scores)
    player_scores.short_description = 'Player Scores'
    referees.short_description = 'Referees'
    list_display = ['name', 'event', 'referees',
                    'id', 'player_scores', 'active']
    search_fields = ['referee__username', 'event__name', 'name']
    fields = ['referee', 'event', 'name', 'active']
    filter_horizontal = ['referee']


@admin.register(PlayerScore)
class PlayerScoreAdmin(GuardedModelAdmin):
    def get_player_name(self, obj):
        return obj.player.__str__()
    # Define um cabeçalho para a coluna
    get_player_name.short_description = 'Player Name'

    list_display = ['get_player_name', 'event', 'sumula', 'points', 'id']
    search_fields = ['event', 'sumula', 'points', 'player']
    fields = ['event', 'sumula', 'points', 'player']


@admin.register(Player)
class PlayerAdmin(GuardedModelAdmin):
    list_display = ['user', 'full_name', 'social_name',
                    'event', 'total_score', 'registration_email', 'id']
    search_fields = ['user', 'total_score', 'event', 'registration_email']
    fields = ['user', 'total_score', 'event',
              'registration_email', 'full_name', 'social_name']

    def username(self, obj):
        return obj.username
    # Optional, to set column header in admin interface.
    username.short_description = 'username'


@admin.register(Staff)
class StaffAdmin(GuardedModelAdmin):
    list_display = ['full_name', 'user', 'event', 'registration_email', 'id']
    search_fields = ['full_name', 'user', 'event', 'registration_email']
    fields = ['full_name', 'user', 'event', 'registration_email', 'is_manager']

    # def username(self, obj):
    #     return obj.username
    # # Optional, to set column header in admin interface.
    # username.short_description = 'username'
