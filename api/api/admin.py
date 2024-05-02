from django.contrib import admin
from .models import Token, Event, Sumula, PlayerScore, PlayerTotalScore


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['token_code', 'id']
    search_fields = ['token_code']
    fields = ['token_code']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['token', 'name', 'id']
    search_fields = ['token', 'name']
    fields = ['token', 'name']


@admin.register(Sumula)
class SumulaAdmin(admin.ModelAdmin):

    def referee():
        referees = []
        for referee in Sumula.referee:
            referees.append(referee)
        return ' '.join(referees)
    list_display = ['event', 'name', 'referee', 'id']
    search_fields = ['referee', 'event', 'name']
    fields = ['referee', 'event', 'name']


@admin.register(PlayerScore)
class PlayerScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'sumula', 'points', 'id']
    search_fields = ['user', 'event', 'sumula', 'points']
    fields = ['user', 'event', 'sumula', 'points']


@admin.register(PlayerTotalScore)
class PlayerTotalScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'event', 'id']
    search_fields = ['user', '_total_points', 'event']
    fields = ['user', 'total_points', 'event']
