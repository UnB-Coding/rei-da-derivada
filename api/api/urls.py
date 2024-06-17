from django.contrib import admin
from django.urls import path, re_path
from .views.views_event import TokenView, EventView
from .views.views_staff import StaffView, AddStaffManager, AddStaffMembers
from .views.views_players import PlayersView, GetPlayerResults, AddPlayers, PublishPlayersResults, Top4Players
from .views.views_sumulas import SumulaView, ActiveSumulaView, FinishedSumulaView, GetSumulaForPlayer, SumulaImortalView, SumulaClassificatoriaView

app_name = 'api'


urlpatterns = [
    # Rotas de evento e token
    path('token/', TokenView.as_view(), name='token'),
    path('event/', EventView.as_view(), name='event'),

    # Rotas de sumula
    path('sumula/', SumulaView.as_view(), name='sumula'),
    path('sumula/imortal/', SumulaImortalView.as_view(), name='sumula-imortal'),
    path('sumula/classificatoria/', SumulaClassificatoriaView.as_view(),
         name='sumula-classificatoria'),
    path('sumula/ativas/', ActiveSumulaView.as_view(), name='sumula-ativas'),
    path('sumula/encerradas/', FinishedSumulaView.as_view(),
         name='sumula-encerradas'),
    path('sumula/player/', GetSumulaForPlayer.as_view(), name='sumula-player'),

    # Rotas de jogadores
    path('players/', PlayersView.as_view(), name='players'),
    path('player/', GetPlayerResults.as_view(), name='player'),
    path('upload-player/', AddPlayers.as_view(), name='upload-player'),
    path('top4/', Top4Players.as_view(), name='top4'),
    path('publish-results/', PublishPlayersResults.as_view(), name='publish-results'),

    # Rotas de staff
    path('staff/', StaffView.as_view(), name='staff'),
    path('staff-manager/', AddStaffManager.as_view(), name='staff-manager'),
    path('upload-staff/', AddStaffMembers.as_view(), name='upload-staff'),
]
