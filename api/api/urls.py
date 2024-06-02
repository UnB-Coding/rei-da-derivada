from django.contrib import admin
from django.urls import path, re_path
from .views.views_event import TokenView, EventView
from .views.views_staff import StaffView, AddStaffManager, AddStaffMembers
from .views.views_players import PlayersView, GetPlayerResults, AddPlayers, PublishPlayersResults, Top4Players
from .views.views_sumulas import SumulaView, ActiveSumulaView, FinishedSumulaView

app_name = 'api'


urlpatterns = [
    path('token/', TokenView.as_view(), name='token'),
    path('event/', EventView.as_view(), name='event'),
    path('sumula/', SumulaView.as_view(), name='sumula'),
    path('sumula/ativas/', ActiveSumulaView.as_view(), name='sumula-ativas'),
    path('sumula/encerradas/', FinishedSumulaView.as_view(),
         name='sumula-encerradas'),
    path('players/', PlayersView.as_view(), name='players'),
    path('player/', GetPlayerResults.as_view(), name='player'),
    path('staff/', StaffView.as_view(), name='staff'),
    path('staff-manager', AddStaffManager.as_view(), name='staff-manager'),
    path('upload-players/', AddPlayers.as_view(), name='upload'),
    path('upload-staff/', AddStaffMembers.as_view(), name='upload-staff'),
    path('top4/', Top4Players.as_view(), name='top4'),
    path('publish-results/', PublishPlayersResults.as_view(), name='publish-results'),
]
