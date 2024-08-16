from django.contrib import admin
from django.urls import path, re_path
from .views.views_event import EventView, ResultsView, PublishFinalResults, PublishImortalsResults, Top3ImortalPlayers
from .views.views_staff import StaffView, AddStaffManager, AddStaffMembers, AddSingleStaff, DeleteAllStaffs
from .views.views_players import PlayersView, GetPlayerResults, AddPlayersExcel, AddSinglePlayer, DeleteAllPlayers
from .views.views_sumulas import GetSumulasView, ActiveSumulaView, FinishedSumulaView, GetSumulaForPlayer, SumulaImortalView, SumulaClassificatoriaView, AddRefereeToSumulaView, GenerateSumulas

app_name = 'api'


urlpatterns = [
    # Rotas de evento e token
    #     path('token/', TokenView.as_view(), name='token'),
    path('event/', EventView.as_view(), name='event'),
    path('results/', ResultsView.as_view(), name='results'),
    path('publish/results/imortals/', PublishImortalsResults.as_view(),
         name='publish-results-imortals'),
    path('publish/results/final',
         PublishFinalResults.as_view(), name='publish-results-final'),

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
    path('top3/', Top3ImortalPlayers.as_view(), name='top3'),
    path('player/add/', AddSinglePlayer.as_view(), name='add-player'),
    path('players/delete/', DeleteAllPlayers.as_view(), name='delete-players'),
    # Rotas de staff
    path('staff/', StaffView.as_view(), name='staff'),
    path('staff/add', AddSingleStaff.as_view(), name='add-staff'),
    path('staff-manager/', AddStaffManager.as_view(), name='staff-manager'),
    path('upload-staff/', AddStaffMembers.as_view(), name='upload-staff'),
    path('staffs/delete/', DeleteAllStaffs.as_view(), name='delete-staffs'),
]
