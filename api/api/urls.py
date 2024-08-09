from django.contrib import admin
from django.urls import path, re_path
from .views.views_event import EventView, ResultsView
from .views.views_staff import StaffView, AddStaffManager, AddStaffMembers, AddSingleStaff, EditStaffData
from .views.views_players import PlayersView, GetPlayerResults, AddPlayersExcel, PublishPlayersResults, Top3ImortalPlayers, AddSinglePlayer
from .views.views_sumulas import GetSumulasView, ActiveSumulaView, FinishedSumulaView, GetSumulaForPlayer, SumulaImortalView, SumulaClassificatoriaView, AddRefereeToSumulaView, GenerateSumulas

app_name = 'api'


urlpatterns = [
    # Rotas de evento e token
    #     path('token/', TokenView.as_view(), name='token'),
    path('event/', EventView.as_view(), name='event'),
    path('results/', ResultsView.as_view(), name='results'),

    # Rotas de sumula
    path('sumula/', GetSumulasView.as_view(), name='sumula'),
    path('sumula/imortal/', SumulaImortalView.as_view(), name='sumula-imortal'),
    path('sumula/classificatoria/', SumulaClassificatoriaView.as_view(),
         name='sumula-classificatoria'),
    path('sumula/ativas/', ActiveSumulaView.as_view(), name='sumula-ativas'),
    path('sumula/encerradas/', FinishedSumulaView.as_view(),
         name='sumula-encerradas'),
    path('sumula/player/', GetSumulaForPlayer.as_view(), name='sumula-player'),
    path('sumula/add-referee/', AddRefereeToSumulaView.as_view(),
         name='sumula-add-referee'),
    path('sumula/generate/', GenerateSumulas.as_view(), name='sumula-generate'),
    # Rotas de jogadores
    path('players/', PlayersView.as_view(), name='players'),
    path('player/', GetPlayerResults.as_view(), name='player'),
    path('upload-player/', AddPlayersExcel.as_view(), name='upload-player'),
    path('top4/', Top3ImortalPlayers.as_view(), name='top4'),
    path('publish-results/', PublishPlayersResults.as_view(), name='publish-results'),
    path('player/add/', AddSinglePlayer.as_view(), name='add-player'),

    # Rotas de staff
    path('staff/', StaffView.as_view(), name='staff'),
    path('staff/add', AddSingleStaff.as_view(), name='add-staff'),
    path('staff/edit', EditStaffData.as_view(), name='edit-staff'),
    path('staff-manager/', AddStaffManager.as_view(), name='staff-manager'),
    path('upload-staff/', AddStaffMembers.as_view(), name='upload-staff'),
]
