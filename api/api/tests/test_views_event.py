
from api.models import Sumula, Token, Event
from users.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from ..utils import get_permissions, get_content_type
from ..serializers import UserSerializer
from guardian.shortcuts import get_perms, assign_perm, remove_perm
from ..permissions import assign_permissions
import uuid
from django.db.models import Q


class TokenViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='testuser', email='example@email.com')
        self.group = Group.objects.create(name='App_Admin')
        self.permission = get_permissions(get_content_type(Token))
        self.group.permissions.set(self.permission)

    def test_create_token(self):
        """Test creating a new token with a valid user."""
        url = reverse('api:token')
        self.client.force_authenticate(user=self.user)
        self.user.groups.add(self.group)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.count(), 1)
        self.assertEqual(Token.objects.get().token_code,
                         response.data['token_code'])

    def test_create_token_unauthenticated(self):
        """Test creating a new token without authentication."""
        url = reverse('api:token')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Token.objects.count(), 0)

    def test_create_token_with_unauthorized_user(self):

        url = reverse('api:token')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Token.objects.count(), 0)

    def tearDown(self):
        self.user.delete()
        self.group.delete()
        self.permission.delete()
        self.client.logout()
        self.client.force_authenticate(user=None)
        if Token.objects.exists():
            Token.objects.all().delete()


class EventViewTest(APITestCase):
    def setUpUser(self):
        self.user = User.objects.create(
            username='testuser', email='test@email.com')
        self.app_admin_user = User.objects.create(
            username='app_admin_user', email='adm@email.com')

    def setUpToken(self):
        self.token = Token.objects.create()
        self.token2 = Token.objects.create()

    def setUpGroups(self):
        self.group_event_admin = Group.objects.create(name='event_admin')
        self.group_app_admin = Group.objects.create(name='app_admin')
        self.app_admin_user.groups.add(self.group_app_admin)

    def setUpPermissions(self):
        self.content_type = ContentType.objects.get_for_model(Event)
        self.permission = Permission.objects.filter(
            content_type=self.content_type)

    def setUpAssignPermissions(self):
        for permission in self.permission:
            assign_perm(permission.codename, self.user, self.event)

    def setUp(self):
        self.setUpUser()
        self.setUpToken()
        self.setUpGroups()
        self.setUpPermissions()
        self.event = Event.objects.create(token=self.token2)
        self.setUpAssignPermissions()

    def test_create_event(self):
        """Test creating a new event with a valid token."""
        url = reverse('api:event')
        data = {'token_code': self.token.token_code}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], '')
        event_id = response.data['id']
        self.assertIsNotNone(event_id)
        self.assertTrue(Event.objects.filter(id=event_id).exists())
        event = Event.objects.get(id=event_id)
        self.assertEqual(event.token, self.token)
        for permission in self.permission:
            if permission.codename != 'add_event':
                self.assertTrue(self.user.has_perm(permission.codename, event))
            else:
                self.assertFalse(self.user.has_perm(
                    permission.codename, event))

    def test_create_event_with_invalid_token_with_authorized_user(self):
        """Test creating a new event with an invalid token."""
        url = reverse('api:event')
        data = {'token_code': 'invalid_token', 'name': 'New Event'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_event_without_token_with_authorized_user(self):
        """Test creating a new event without a token."""
        url = reverse('api:event')
        data = {'name': 'New Event'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_event_unauthenticated(self):
        """Test creating a new event without authentication."""
        url = reverse('api:event')
        data = {'token_code': self.token.token_code, 'name': 'New Event'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_event_with_existing_token_with_authorized_user(self):
        """Test creating a new event with a token that already has an associated event."""
        self.token.mark_as_used()

        url = reverse('api:event')
        data = {'token_code': self.token.token_code, 'name': 'New Event'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_event_with_authorized_user(self):
        """Test deleting an existing event with a valid token."""
        url = reverse('api:event')
        data = {'token_code': self.token2.token_code}
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_event_without_associated_event_with_authorized_user(self):
        """Test deleting an event without an associated event."""
        url = reverse('api:event')
        data = {'token_code': self.token.token_code}
        # print("Permissões do usuário:", self)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_event_unauthenticated(self):
        """Test deleting an event without authentication."""
        url = reverse('api:event')
        data = {'token_code': self.token.token_code}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_event_with_unauthorized_user(self):
        """Test deleting an event with an unauthorized user."""
        url = reverse('api:event')
        data = {'token_code': self.token2.token_code}

        remove_perm('delete_event', self.user, self.event)
        self.client.force_authenticate(user=self.user)  # type: ignore

        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_with_app_admin_user(self):
        """Test deleting an event with an app admin user."""
        url = reverse('api:event')
        data = {'token_code': self.token2.token_code}
        self.client.force_authenticate(user=self.app_admin_user)
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        self.user.delete()
        self.token.delete()
        self.token.token_code = None
        self.app_admin_user.delete()
        self.event.delete()
        self.group_app_admin.delete()
        self.group_event_admin.delete()
        self.permission.delete()
        self.client.logout()
        self.client.force_authenticate(user=None)
        if Event.objects.exists():
            Event.objects.all().delete()


class StaffViewTest(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUpResponseData(self):
        self.response_data_total = UserSerializer(
            [self.user_staff1, self.user_staff2], many=True).data
        self.response_data_staff1 = UserSerializer(
            [self.user_staff1], many=True).data

    def setUpUser(self):
        self.user_staff1 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='Staff1', last_name='Member1')
        self.user_staff2 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='Staff2', last_name='Member2')
        self.admin = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='Admin', last_name='User')

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpGroup(self):
        self.group = Group.objects.create(name='staff_member')
        self.group2 = Group.objects.create(name='staff_manager')
        self.group3 = Group.objects.create(name='app_admin')
        self.group4 = Group.objects.create(name='event_admin')
        self.user_staff1.groups.add(self.group)
        self.user_staff2.groups.add(self.group)
        self.admin.groups.add(self.group4)

    def setUpPermissions(self):
        self.content_type = ContentType.objects.get_for_model(Event)
        self.permission = Permission.objects.filter(
            content_type=self.content_type).filter(Q(codename__icontains='view') | Q(codename__icontains='change')).exclude(codename__icontains='change_event')
        assign_permissions(self.admin, self.group4, self.event)

    def setUp(self):
        self.setUpEvent()
        self.setUpUser()
        self.setUpGroup()
        self.setUpPermissions()
        self.setUpResponseData()

    def test_add_staff_member(self):
        """Test adding a staff member to an event."""
        url = reverse('api:staff')
        data = {'token_code': self.token.token_code}
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user_staff1.events.count(), 1)
        for permission in self.permission:
            self.assertTrue(self.user_staff1.has_perm(
                permission.codename, self.event))

    def test_add_staff_member_without_token(self):
        """Test adding a staff member without a token."""
        url = reverse('api:staff')
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_member_with_invalid_token(self):
        """Test adding a staff member with an invalid token."""
        url = reverse('api:staff')
        data = {'token_code': 'invalid_token'}
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_member_with_unauthenticated_user(self):
        """Test adding a staff member without authentication."""
        url = reverse('api:staff')
        data = {'token_code': self.token.token_code}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_staff_members(self):
        """Test getting staff members from an event."""
        self.user_staff1.events.add(self.event)
        self.user_staff2.events.add(self.event)
        url = f'{reverse("api:staff")}?event_id={self.event.id}'
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.response_data_total)

    def test_get_staff_members_exlcuding_other_groups(self):
        """Test getting staff members from an event excluding other groups."""
        self.user_staff1.events.add(self.event)
        self.user_staff2.events.add(self.event)
        self.user_staff2.groups.add(self.group2, self.group3, self.group4)
        url = f'{reverse("api:staff")}?event_id={self.event.id}'
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data, self.response_data_total)
        self.assertNotIn(self.user_staff2, response.data)
        self.assertEqual(response.data, self.response_data_staff1)

    def test_get_staff_members_without_event_id(self):
        """Test getting staff members without an event id."""
        url = reverse('api:staff')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_staff_members_with_unauthenticated_user(self):
        """Test getting staff members without authentication."""
        url = f'{reverse("api:staff")}?event_id={self.event.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_staff_members_with_unauthorized_user(self):
        """Test getting staff members with an unauthorized user."""
        url = f'{reverse("api:staff")}?event_id={self.event.id}'
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        User.objects.all().delete()
        Event.objects.all().delete()
        Group.objects.all().delete()
        Permission.objects.all().delete()
        self.client.logout()
        self.client.force_authenticate(user=None)
        if Token.objects.exists():
            Token.objects.all().delete()


class AddStaffManagerTestCase(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUpUser(self):
        self.user = User.objects.create(username='staff_member', email=self.create_unique_email(
        ), first_name='Staff', last_name='Member')
        self.admin = User.objects.create(username='event_admin', email=self.create_unique_email(
        ), first_name='Event', last_name='Admin')

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpGroup(self):
        self.group = Group.objects.create(name='staff_member')
        self.group2 = Group.objects.create(name='staff_manager')
        self.group3 = Group.objects.create(name='app_admin')
        self.group4 = Group.objects.create(name='event_admin')
        self.admin.groups.add(self.group4)

    def setUpPermissions(self):
        self.content_type = ContentType.objects.get_for_model(Event)
        self.permission = Permission.objects.filter(
            content_type=self.content_type).filter(Q(codename__icontains='view') | Q(codename__icontains='change')).exclude(codename__icontains='change_event')
        assign_permissions(self.admin, self.group4, self.event)

    def setUp(self):
        self.setUpUser()
        self.setUpEvent()
        self.setUpGroup()
        self.setUpPermissions()
        self.data = {'id': self.user.id, 'email': self.user.email}
        self.url = f'{reverse("api:staff-manager")}?event_id={self.event.id}'

    def test_add_staff_manager(self):
        """Test adding a staff manager to an event."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.groups.filter(name='staff_manager').exists())
        for permission in self.permission:
            self.assertTrue(self.user.has_perm(
                permission.codename, self.event))

    def test_add_staff_manager_without_event_id(self):
        """Test adding a staff manager without an event id."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse('api:staff-manager'), self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_manager_with_unauthenticated_user(self):
        """Test adding a staff manager without authentication."""
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_staff_manager_with_unauthorized_user(self):
        """Test adding a staff manager with an unauthorized user."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_staff_manager_with_invalid_event_id(self):
        """Test adding a staff manager with an invalid event id."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f'{reverse("api:staff-manager")}?event_id=invalid_id', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        User.objects.all().delete()
        Event.objects.all().delete()
        Group.objects.all().delete()
        Permission.objects.all().delete()
        self.client.logout()
        self.client.force_authenticate(user=None)
        if Token.objects.exists():
            Token.objects.all().delete()
