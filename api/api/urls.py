from django.contrib import admin
from django.urls import path, include
from .views.views_event import TokenView, EventView, StaffView
from .views.views_players import PlayersView, GetCurrentPlayer
from .views.views_sumulas import SumulaView, ActiveSumulaView

app_name = 'api'


urlpatterns = [
    path('token/', TokenView.as_view(), name='token'),
    path('event/', EventView.as_view(), name='event'),
    path('sumula/', SumulaView.as_view(), name='sumula'),
    path('sumula/ativas/', ActiveSumulaView.as_view(), name='sumula-ativas'),
    path('players/', PlayersView.as_view(), name='players'),
    path('player/', GetCurrentPlayer.as_view(), name='player'),
    path('staff/', StaffView.as_view(), name='staff')
]
