from django import forms
from django.contrib import admin
from django.forms import ValidationError
from .models import Token, Event, SumulaImortal, SumulaClassificatoria, PlayerScore, Player, Staff
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
    list_display = ['id', 'token', 'staff_token',
                    'players_token', 'name', 'active']
    search_fields = ['token', 'name', 'active']
    fields = ['token', 'name', 'active']


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


@admin.register(SumulaImortal)
class SumulaImortalAdmin(SumulaAdmin):
    pass


@admin.register(SumulaClassificatoria)
class SumulaClassificatoriaAdmin(SumulaAdmin):
    pass


class PlayerScoreForm(forms.ModelForm):
    class Meta:
        model = PlayerScore
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        sumula_classificatoria = cleaned_data.get("sumula_classificatoria")
        sumula_imortal = cleaned_data.get("sumula_imortal")

        # Verifica se ambas ou nenhuma das súmulas estão preenchidas
        if sumula_classificatoria and sumula_imortal:
            raise ValidationError(
                "Um jogador não pode estar em duas súmulas ao mesmo tempo.")
        elif not sumula_classificatoria and not sumula_imortal:
            raise ValidationError(
                "Um jogador deve estar em pelo menos uma súmula.")

        return cleaned_data

# Atualize a classe PlayerScoreAdmin para usar o ModelForm personalizado


@admin.register(PlayerScore)
class PlayerScoreAdmin(GuardedModelAdmin):
    form = PlayerScoreForm

    def get_player_name(self, obj):
        return obj.player.__str__()
    get_player_name.short_description = 'Player Name'

    list_display = ['get_player_name', 'event', 'sumula_classificatoria',
                    'sumula_imortal', 'points', 'id']
    search_fields = ['event', 'sumula_classificatoria',
                     'sumula_imortal', 'points', 'player']
    fields = ['event', 'sumula_classificatoria',
              'sumula_imortal', 'points', 'player']


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
