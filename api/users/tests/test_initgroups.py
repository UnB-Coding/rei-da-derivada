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
        GROUPS = "App_Admin,Event_Admin,Staff_Manager,Staff_Member,Player"
        self.command.handle()
        for group_name in GROUPS.split(','):
            self.assertTrue(Group.objects.filter(name=group_name).exists())

    def test_content_type(self):
        """ Testa se os content types estão corretos."""
        content_type_event = self.command.get_content_type(Event)
        content_type_sumula = self.command.get_content_type(Sumula)
        self.assertEqual(content_type_event,
                         ContentType.objects.get_for_model(Event))
        self.assertEqual(content_type_sumula,
                         ContentType.objects.get_for_model(Sumula))

    def test_permissions(self):
        """ Testa se as permissões estão sendo criadas."""
        group = Group.objects.create(name='App_Admin')
        self.command.add_permissions(group)
        self.assertTrue(group.permissions.exists())

    def test_permissions_App_Admin(self):
        """ Testa se as permissões do grupo App_Admin estão corretas.
        O grupo App_Admin deve ter todas as permissões.
        """
        group = Group.objects.create(name='App_Admin')
        self.command.add_permissions(group)

        for key in self.command.permissions:
            for permission in self.command.permissions[key]:
                self.assertTrue(group.permissions.filter(
                    codename=permission.codename).exists())

    def test_permissions_Event_Admin(self):
        """ Testa se as permissões do grupo Event_Admin estão corretas.
        O grupo Event_Admin deve ter permissões de alterar, deletar e visualizar eventos e todas as permissões de sumula, player_score e player.
        """
        group = Group.objects.create(name='Event_Admin')
        self.command.add_permissions(group)

        should_exist = {
            'event': lambda permission: 'change' in permission.codename or 'delete' in permission.codename or 'view' in permission.codename,
            'sumula': lambda permission: True,
            'player_score': lambda permission: True,
            'player': lambda permission: True,
            'token': lambda permission: False,
        }

        for key in self.command.permissions:
            for permission in self.command.permissions[key]:
                if should_exist[key](permission):
                    self.assertTrue(group.permissions.filter(
                        codename=permission.codename).exists())
                else:
                    self.assertFalse(group.permissions.filter(
                        codename=permission.codename).exists())

    def test_permissions_Staff_Manager(self):
        group = Group.objects.create(name='Staff_Manager')
        self.command.add_permissions(group)

        should_exist = {
            'event': lambda permission: 'view' in permission.codename,
            'sumula': lambda permission: True,
            'player_score': lambda permission: True,
            'player': lambda permission: 'view' in permission.codename or 'change' in permission.codename,
            'token': lambda permission: False,
        }

        for key in self.command.permissions:
            for permission in self.command.permissions[key]:
                if should_exist[key](permission):
                    self.assertTrue(group.permissions.filter(
                        codename=permission.codename).exists())
                else:
                    self.assertFalse(group.permissions.filter(
                        codename=permission.codename).exists())

    def test_permissions_Staff_Member(self):
        group = Group.objects.create(name='Staff_Member')
        self.command.add_permissions(group)

        should_exist = {
            'event': lambda permission: 'view' in permission.codename,
            'sumula': lambda permission: 'change' in permission.codename or 'view' in permission.codename,
            'player_score': lambda permission: 'view' in permission.codename or 'change' in permission.codename,
            'player': lambda permission: 'view' in permission.codename or 'change' in permission.codename,
            'token': lambda permission: False,
        }
        for key in self.command.permissions:
            for permission in self.command.permissions[key]:
                if should_exist[key](permission):
                    self.assertTrue(group.permissions.filter(
                        codename=permission.codename).exists())
                else:
                    self.assertFalse(group.permissions.filter(
                        codename=permission.codename).exists())

    def test_permissions_Player(self):
        group = Group.objects.create(name='Player')
        self.command.add_permissions(group)

        should_exist = {
            'event': lambda permission: 'view' in permission.codename,
            'sumula': lambda permission: False,
            'player_score': lambda permission: 'view' in permission.codename,
            'player': lambda permission: 'view' in permission.codename,
            'token': lambda permission: False,
        }
        for key in self.command.permissions:
            for permission in self.command.permissions[key]:
                if should_exist[key](permission):
                    self.assertTrue(group.permissions.filter(
                        codename=permission.codename).exists())
                else:
                    self.assertFalse(group.permissions.filter(
                        codename=permission.codename).exists())
