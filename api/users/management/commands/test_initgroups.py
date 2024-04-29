from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
import six
from io import StringIO
from django.core.management import call_command
from api.models import Event, Sumula, PlayerScore, PlayerTotalScore, Token


class InitGroupsTest(TestCase):
    def setUp(self):
        self.stdout = StringIO()

    def test_handle_command(self):
        call_command('initgroups', stdout=self.stdout)
        output = self.stdout.getvalue()
        self.assertIn('Grupo Owners criado!', output)
        self.assertIn('Grupo Event_Admin criado!', output)
        self.assertIn('Grupo Staff_Manager criado!', output)
        self.assertIn('Grupo Staff_Member criado!', output)
        self.assertIn('Grupo Player criado!', output)

    def test_group_permissions(self):
        call_command('initgroups')

        owners_group = Group.objects.get(name='Owners')
        event_admin_group = Group.objects.get(name='Event_Admin')
        staff_manager_group = Group.objects.get(name='Staff_Manager')
        staff_member_group = Group.objects.get(name='Staff_Member')
        player_group = Group.objects.get(name='Player')

        self.assertEqual(owners_group.permissions.count(), 5)
        self.assertEqual(event_admin_group.permissions.count(), 4)
        self.assertEqual(staff_manager_group.permissions.count(), 4)
        self.assertEqual(staff_member_group.permissions.count(), 4)
        self.assertEqual(player_group.permissions.count(), 3)

        self.assertTrue(owners_group.permissions.filter(
            codename__icontains='change').exists())
        self.assertTrue(owners_group.permissions.filter(
            codename__icontains='delete').exists())
        self.assertTrue(owners_group.permissions.filter(
            codename__icontains='view').exists())

        self.assertTrue(event_admin_group.permissions.filter(
            codename__icontains='change').exists())
        self.assertTrue(event_admin_group.permissions.filter(
            codename__icontains='delete').exists())
        self.assertTrue(event_admin_group.permissions.filter(
            codename__icontains='view').exists())

        self.assertTrue(staff_manager_group.permissions.filter(
            codename__icontains='view').exists())
        self.assertTrue(staff_manager_group.permissions.filter(
            codename__icontains='change').exists())

        self.assertTrue(staff_member_group.permissions.filter(
            codename__icontains='view').exists())
        self.assertTrue(staff_member_group.permissions.filter(
            codename__icontains='change').exists())

        self.assertTrue(player_group.permissions.filter(
            codename__icontains='view').exists())

    def tearDown(self):
        self.stdout.close()
        Group.objects.all().delete()
        Permission.objects.all().delete()
        ContentType.objects.all().delete()
        Event.objects.all().delete()
        Sumula.objects.all().delete()
        PlayerScore.objects.all().delete()
        PlayerTotalScore.objects.all().delete()
        Token.objects.all().delete()
