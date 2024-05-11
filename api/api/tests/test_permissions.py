from django.contrib.auth.models import Permission, Group
from users.models import User
from ..models import Event, Token
from ..permissions import filter_permissions, assign_permissions
import uuid
from django.db.models import QuerySet
from django.test import TestCase

event_admin_permissions = ['change_event', 'view_event', 'delete_event', 'add_sumula_event', 'change_sumula_event', 'delete_sumula_event', 'view_sumula_event', 'add_player_event',
                           'change_player_event', 'view_player_event', 'delete_player_event', 'add_player_score_event', 'change_player_score_event', 'view_player_score_event', 'delete_player_score_event']
staff_manager_permissions = [perm for perm in event_admin_permissions if perm not in [
    'delete_event', 'change_event', 'delete_player_event']]
staff_member_permissions = [perm for perm in staff_manager_permissions if perm not in [
    'add_sumula_event', 'delete_sumula_event', 'add_player_event', 'delete_player_event', 'add_player_score_event', 'delete_player_score_event']]
player_permissions = ['view_event', 'view_sumula_event',
                      'view_player_event', 'view_player_score_event']
EXPECTED_PERMISSIONS = {
    "event_admin": event_admin_permissions,
    "staff_manager": staff_manager_permissions,
    "staff_member": staff_member_permissions,
    "player": player_permissions,
}


class AddPermissionsTestCase(TestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUpGroups(self):
        for group_name in EXPECTED_PERMISSIONS.keys():
            group = Group.objects.create(name=group_name)
            setattr(self, f'group_{group_name}', group)

    def setUpUser(self):
        self.user = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email())

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUp(self):
        self.setUpEvent()
        self.setUpGroups()
        self.setUpUser()

    def test_filter_permissions_groups(self):
        """Testa a atribuição de permissões aos grupos."""
        for group_name, expected_permissions in EXPECTED_PERMISSIONS.items():
            group = getattr(self, f'group_{group_name}')
            permissions = filter_permissions(group)
            self.assertIsNotNone(permissions)
            self.assertIsInstance(permissions, QuerySet[Permission])
            for permission in permissions:
                self.assertTrue(permission.codename in expected_permissions)

    def test_assign_permissions(self):
        """Testa a atribuição de permissões ao usuário."""
        for group_name, expected_permissions in EXPECTED_PERMISSIONS.items():
            group = getattr(self, f'group_{group_name}')
            assign_permissions(self.user, group, self.event)
            self.verify_permissions(
                self.user, self.event, expected_permissions)

    def test_filter_permissions_invalid_group(self):
        invalid_group = Group.objects.create(name='invalid_group')
        permissions = filter_permissions(invalid_group)
        self.assertIsNone(permissions)

    def verify_permissions(self, user, obj, expected_permissions):
        for perm in expected_permissions:
            self.assertTrue(user.has_perm(perm, obj))

    def tearDown(self):
        self.event.delete()
        self.token.delete()
        self.user.delete()
        if Group.objects.all().exists():
            Group.objects.all().delete()
