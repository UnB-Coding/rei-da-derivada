from django.contrib import admin
from .models import Token, Event, Sumula, PlayerScore, Player


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
    list_display = ['event', 'sumula', 'points', 'id']
    search_fields = ['event', 'sumula', 'points']
    fields = ['event', 'sumula', 'points']


@admin.register(Player)
class Admin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'event',
                    'total_score', 'registration_email', 'id']
    search_fields = ['first_name', 'last_name',
                     'total_score', 'event', 'registration_email']
    fields = ['user', 'total_score', 'event', 'registration_email']
