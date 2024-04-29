from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from unittest.mock import patch
from api.models import Event, Sumula, PlayerScore, PlayerTotalScore, Token
from ..management.commands.initgroups import Command
from django.contrib.auth.models import Group


class CreateGroupsTestCase(TestCase):
    def setUp(self):
        self.command = Command()

    @patch('builtins.print')
    def test_group_creation(self, mock_print):
        GROUPS = "Owners,Event_Admin,Staff_Manager,Staff_Member,Player"
        self.command.handle()
        for group_name in GROUPS.split(','):
            self.assertTrue(Group.objects.filter(name=group_name).exists())
            mock_print.assert_any_call(f'Grupo {group_name} criado!')

    def test_content_type(self):
        content_type_event = self.command.get_content_type(Event)
        content_type_sumula = self.command.get_content_type(Sumula)
        self.assertEqual(content_type_event,
                         ContentType.objects.get_for_model(Event))
        self.assertEqual(content_type_sumula,
                         ContentType.objects.get_for_model(Sumula))

    def test_permissions(self):
        group = Group.objects.create(name='Owners')
        self.command.add_permissions(group)
        self.assertTrue(group.permissions.exists())

    def test_permissions_owners(self):
        group = Group.objects.create(name='Owners')
        self.command.add_permissions(group)
        self.assertTrue(group.permissions.filter(
            codename='add_event').exists())
        self.assertTrue(group.permissions.filter(
            codename='change_event').exists())
        # Add assertions for other permissions as needed
