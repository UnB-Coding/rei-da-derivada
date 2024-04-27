from django.core.management.base import BaseCommand
from decouple import config
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from decouple import config
from api.models import Event, Sumula, PlayerScore, PlayerTotalScore
GROUPS = ["Owners,Event_Admin,Staff_Manager,Staff_Member,Player"]


class Command(BaseCommand):
    """Este comando cria os grupos de usuários no banco de dados."""

    def handle(self, *args, **options):
        for group in config('GROUPS').split(','):
            if not len(Group.objects.all().filter(name=group)):
                self.group_created = Group.objects.create(name=group)
                print(f'Grupo {group} criado!')
            else:
                print(f'Grupo {group} já existe!')
            self.add_permissions(self.group_created)

    def add_permissions(self, *args, **options):
        """Adiciona diferentes níveis de permissão aos grupos de usuários.
        para as models de Event,Sumula,PlayerScore e PlayerTotalScore."""
        group = args[0]
        event_content_type = ContentType.objects.get_for_model(Event)
        sumula_content_type = ContentType.objects.get_for_model(Sumula)
        player_score_content_type = ContentType.objects.get_for_model(
            PlayerScore)
        player_total_score_content_type = ContentType.objects.get_for_model(
            PlayerTotalScore)
        event_permissions = Permission.objects.filter(
            content_type=event_content_type)
        print(event_permissions)
        sumula_permissions = Permission.objects.filter(
            content_type=sumula_content_type)
        player_score_permissions = Permission.objects.filter(
            content_type=player_score_content_type)
        player_total_score_permissions = Permission.objects.filter(
            content_type=player_total_score_content_type)

        if group == "Owners":
            permissions = event_permissions | sumula_permissions | player_score_permissions | player_total_score_permissions
            group.permissions.set(permissions)
            print(f'Permissões adicionadas com sucesso! {group}')

        elif group.name == "Event_Admin":
            permissions = event_permissions.filter(
                Q(codename__icontains='change') |
                Q(codename__icontains='delete') |
                Q(codename__icontains='view')) | sumula_permissions | player_score_permissions | player_total_score_permissions
            group.permissions.set(permissions)
            print(f'Permissões adicionadas com sucesso! {group}')
        elif group.name == "Staff_Manager":
            permissions = event_permissions.filter(
                Q(codename__icontains='view')) | sumula_permissions.filter | player_score_permissions | player_total_score_permissions
            group.permissions.set(permissions)
        elif group.name == "Staff_Member":
            permissions = event_permissions.filter(
                Q(codename__icontains='view')) | sumula_permissions.filter(Q(codename__icontains='change') | Q(codename__icontains="view")) | player_score_permissions.filter | player_total_score_permissions
            group.permissions.set(permissions)

        elif group.name == "Player":
            permissions = event_permissions.filter(
                Q(codename__icontains='view')) | player_score_permissions.filter(Q(codename__icontains='view')) | player_total_score_permissions.filter(Q(codename__icontains='view'))
            group.permissions.set(permissions)
        print('Permissões adicionadas com sucesso!')

    def add_owner_permissions(self, group: Group, *args, **options):
        """Adiciona permissões de Owner ao grupo Owners."""
