from django.contrib import admin
from .models import Token, Event, Sumula, PlayerScore, PlayerTotalScore

# Register your models here.


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['token_code']
    search_fields = ['token_code']
    fields = ['token_code']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['token']
    search_fields = ['token']
    fields = ['token']


@admin.register(Sumula)
class SumulaAdmin(admin.ModelAdmin):
    list_display = ['event', 'name']
    search_fields = ['referee', 'event', 'name']
    fields = ['referee', 'event', 'name']


@admin.register(PlayerScore)
class PlayerScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'sumula', 'points']
    search_fields = ['user', 'event', 'sumula', 'points']
    fields = ['user', 'event', 'sumula', 'points']


@admin.register(PlayerTotalScore)
class PlayerTotalScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'event']
    search_fields = ['user', '_total_points', 'event']
    fields = ['user', 'total_points', 'event']
