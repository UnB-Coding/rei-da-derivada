from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from unittest.mock import patch
from api.models import Event, Sumula, PlayerScore, Player, Token
from ..management.commands.initgroups import Command
from django.contrib.auth.models import Group
from django.db.models import Q


class CreateGroupsTestCase(TestCase):
    def setUp(self):
        self.command = Command()
        self.command.content_types = {
            'event': self.command.get_content_type(Event),
            'sumula': self.command.get_content_type(Sumula),
            'player_score': self.command.get_content_type(PlayerScore),
            'player': self.command.get_content_type(Player),
            'token': self.command.get_content_type(Token),
        }

        self.command.permissions = {
            'event': self.command.get_permissions(self.command.content_types['event']),
            'sumula': self.command.get_permissions(self.command.content_types['sumula']),
            'player_score': self.command.get_permissions(self.command.content_types['player_score']),
            'player': self.command.get_permissions(self.command.content_types['player']),
            'token': self.command.get_permissions(self.command.content_types['token']),
        }

    @patch('builtins.print')
    def test_group_creation(self, mock_print):
        """ Testa se os grupos são criados corretamente."""
        GROUPS = "app_admin,event_admin,staff_manager,staff_member,player"
        self.command.handle()
        for group_name in GROUPS.split(','):
            self.assertTrue(Group.objects.filter(name=group_name).exists())

    @patch('builtins.print')
    def test_content_type(self, mock_print):
        """ Testa se os content types estão corretos."""
        content_type_event = self.command.get_content_type(Event)
        content_type_sumula = self.command.get_content_type(Sumula)
        self.assertEqual(content_type_event,
                         ContentType.objects.get_for_model(Event))
        self.assertEqual(content_type_sumula,
                         ContentType.objects.get_for_model(Sumula))

    @patch('builtins.print')
    def test_permissions(self, mock_print):
        """ Testa se as permissões estão sendo criadas."""
        group = Group.objects.create(name='app_admin')
        self.command.add_permissions(group)
        self.assertTrue(group.permissions.exists())

    @patch('builtins.print')
    def test_permissions_App_Admin(self, mock_print):
        """ Testa se as permissões do grupo App_Admin estão corretas.
        O grupo App_Admin deve ter todas as permissões.
        """
        group = Group.objects.create(name='app_admin')
        self.command.add_permissions(group)

        for key in self.command.permissions:
            for permission in self.command.permissions[key]:
                self.assertTrue(group.permissions.filter(
                    codename=permission.codename).exists())
