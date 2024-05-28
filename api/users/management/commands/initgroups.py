from django.core.management.base import BaseCommand
from decouple import config
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from decouple import config
from api.models import Event, Sumula, PlayerScore, Player, Token
GROUPS = "app_admin,event_admin,staff_manager,staff_member,player"


class Command(BaseCommand):
    """Este comando cria os grupos de usuários no banco de dados."""

    def handle(self, *args, **options):
        for group in GROUPS.split(','):
            self.group, created = Group.objects.get_or_create(name=group)
            if not created:
                print(f'Grupo {group} já existe!')
            else:
                print(f'Grupo {group} criado com sucesso!')
            if self.group.name == 'app_admin':
                self.add_permissions(self.group)

    def add_permissions(self, *args, **options):
        group = args[0]
        print(f'Adicionando permissões ao grupo {group.name}...')

        content_types = {
            'event': self.get_content_type(Event),
            'sumula': self.get_content_type(Sumula),
            'player_score': self.get_content_type(PlayerScore),
            'player': self.get_content_type(Player),
            'token': self.get_content_type(Token),
        }

        permissions = {
            'event': self.get_permissions(content_types['event']),
            'sumula': self.get_permissions(content_types['sumula']),
            'player_score': self.get_permissions(content_types['player_score']),
            'player': self.get_permissions(content_types['player']),
            'token': self.get_permissions(content_types['token']),
        }

        group_permissions = {
            "app_admin": permissions['event'] | permissions['sumula'] | permissions['player_score'] | permissions['player'] | permissions['token'],
        }

        if group.name in group_permissions:
            group.permissions.set(group_permissions[group.name])
            group.save()

    def get_content_type(self, model):
        return ContentType.objects.get_for_model(model)

    def get_permissions(self, content_type):
        return Permission.objects.filter(content_type=content_type)
