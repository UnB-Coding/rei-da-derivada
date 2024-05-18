from django.contrib import admin
from .models import Token, Event, Sumula, PlayerScore, Player
from guardian.admin import GuardedModelAdmin


@admin.register(Token)
class TokenAdmin(GuardedModelAdmin):
    list_display = ['token_code', 'id']
    search_fields = ['token_code']
    fields = ['token_code']


@admin.register(Event)
class EventAdmin(GuardedModelAdmin):
    list_display = ['token', 'name', 'id']
    search_fields = ['token', 'name']
    fields = ['token', 'name']


@admin.register(Sumula)
class SumulaAdmin(GuardedModelAdmin):

    def referee(self, obj):
        referees = []
        for referee in obj.referee.all():
            referees.append(str(referee))
        return ', '.join(referees)

    def player_scores(self, obj):
        scores = []
        for score in obj.scores.all():
            scores.append(f'{score.player.user.__str__()}: {score.points}')
        return ', '.join(scores)
    player_scores.short_description = 'Player Scores'

    list_display = ['event', 'name', 'referee',
                    'id', 'player_scores', 'active']
    search_fields = ['referee__username', 'event__name', 'name']
    fields = ['referee', 'event', 'name']

    """ def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        return readonly_fields + ['player_scores'] """


@admin.register(PlayerScore)
class PlayerScoreAdmin(GuardedModelAdmin):
    def get_player_name(self, obj):
        return obj.player.user.__str__()
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
