from django.core.management.base import BaseCommand
from decouple import config
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from decouple import config
from api.models import Event, Sumula, PlayerScore, PlayerTotalScore, Token
GROUPS = "Owners,Event_Admin,Staff_Manager,Staff_Member,Player"


class Command(BaseCommand):
    """Este comando cria os grupos de usuários no banco de dados."""

    def handle(self, *args, **options):
        for group in GROUPS.split(','):
            if not Group.objects.filter(name=group).exists():
                self.group = Group.objects.create(name=group)
                """ print(f'Grupo {group} criado!') """
            else:
                self.group = Group.objects.get(name=group)
            self.add_permissions(self.group)

    def add_permissions(self, *args, **options):
        group = args[0]
        """ print(f'Adicionando permissões ao grupo {group.name}...') """

        content_types = {
            'event': self.get_content_type(Event),
            'sumula': self.get_content_type(Sumula),
            'player_score': self.get_content_type(PlayerScore),
            'player_total_score': self.get_content_type(PlayerTotalScore),
            'token': self.get_content_type(Token),
        }

        permissions = {
            'event': self.get_permissions(content_types['event']),
            'sumula': self.get_permissions(content_types['sumula']),
            'player_score': self.get_permissions(content_types['player_score']),
            'player_total_score': self.get_permissions(content_types['player_total_score']),
            'token': self.get_permissions(content_types['token']),
        }

        group_permissions = {
            "Owners": permissions['event'] | permissions['sumula'] | permissions['player_score'] | permissions['player_total_score'] | permissions['token'],
            "Event_Admin": permissions['event'].filter(Q(codename__icontains='change') | Q(codename__icontains='delete') | Q(codename__icontains='view')) | permissions['sumula'] | permissions['player_score'] | permissions['player_total_score'],
            "Staff_Manager": permissions['event'].filter(Q(codename__icontains='view')) | permissions['sumula'] | permissions['player_score'] | permissions['player_total_score'].filter(Q(codename__icontains='view') | Q(codename__icontains='change')),
            "Staff_Member": permissions['event'].filter(Q(codename__icontains='view')) | permissions['sumula'].filter(Q(codename__icontains='change') | Q(codename__icontains="view")) | permissions['player_score'].filter(Q(codename__icontains='view') | Q(codename__icontains='change')) | permissions['player_total_score'].filter(Q(codename__icontains='view') | Q(codename__icontains='change')),
            "Player": permissions['event'].filter(Q(codename__icontains='view')) | permissions['player_score'].filter(Q(codename__icontains='view')) | permissions['player_total_score'].filter(Q(codename__icontains='view')),
        }

        if group.name in group_permissions:
            group.permissions.set(group_permissions[group.name])
            """ print(f'Permissões adicionadas com sucesso! {group}')
            permissions_list = group_permissions[group.name].values_list(
                "name", flat=True)
            print(f'Permissões do grupo: {permissions_list}') """

    def get_content_type(self, model):
        return ContentType.objects.get_for_model(model)

    def get_permissions(self, content_type):
        return Permission.objects.filter(content_type=content_type)
