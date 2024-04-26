from django.core.management.base import BaseCommand
from decouple import config
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.contrib.auth.models import User
from decouple import config
GROUPS = ["Owners,Staff_Manager,Staff_Member,Player"]


class Command(BaseCommand):
    """Este comando cria os grupos de usuários no banco de dados."""

    def handle(self, *args, **options):

        for group in config('GROUPS').split(','):
            if not len(Group.objects.all().filter(name=group)):
                Group.objects.create(name=group)
                print(f'Grupo {group} criado!')
            else:
                print(f'Grupo {group} já existe!')

    def add_permissions(self, *args, **options):
        """Adiciona diferentes níveis de permissão aos grupos de usuários."""
        for group in config('GROUPS').split(','):
            group = Group.objects.get(name=group)
            
        print('Permissões adicionadas com sucesso!')
