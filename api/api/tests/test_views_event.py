
from api.models import Token, Event
from users.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from ..utils import get_permissions, get_content_type
from guardian.shortcuts import assign_perm, remove_perm
from ..serializers import UserEventsSerializer


# class TokenViewTest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create(
#             username='testuser', email='example@email.com')
#         self.group = Group.objects.create(name='App_Admin')
#         self.permission = get_permissions(get_content_type(Token))
#         self.group.permissions.set(self.permission)

#     def test_create_token(self):
#         """Test creating a new token with a valid user."""
#         url = reverse('api:token')
#         self.client.force_authenticate(user=self.user)
#         self.user.groups.add(self.group)
#         response = self.client.post(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(Token.objects.count(), 1)
#         self.assertEqual(Token.objects.get().token_code,
#                          response.data['token_code'])

#     def test_create_token_unauthenticated(self):
#         """Test creating a new token without authentication."""
#         url = reverse('api:token')
#         response = self.client.post(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(Token.objects.count(), 0)

#     def test_create_token_with_unauthorized_user(self):

#         url = reverse('api:token')
#         self.client.force_authenticate(user=self.user)
#         response = self.client.post(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(Token.objects.count(), 0)

#     def tearDown(self):
#         self.user.delete()
#         self.group.delete()
#         self.permission.delete()
#         self.client.logout()
#         self.client.force_authenticate(user=None)
#         if Token.objects.exists():
#             Token.objects.all().delete()


class EventViewTest(APITestCase):

    def setUpData(self):
        self.expected_data = UserEventsSerializer(
            [{'event': self.event, 'role': 'admin'}], many=True).data

    def setUpUser(self):
        self.user = User.objects.create(
            username='testuser', email='test@email.com')
        self.event_admin_user = User.objects.create(
            username='event_admin_user', email='adm@email.com')

    def setUpToken(self):
        self.token = Token.objects.create()
        self.token2 = Token.objects.create()

    def setUpGroups(self):
        self.group_event_admin = Group.objects.create(name='event_admin')
        self.event_admin_user.groups.add(self.group_event_admin)

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
        self.setUpData()
        self.event.admin_email = self.user.email
        self.event.save()

    def test_create_event(self):
        """Test creating a new event with a valid token."""
        url = reverse('api:event')
        data = {'token_code': self.token.token_code,
                'name': 'New Event',
                }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Event')
        self.assertEqual(self.user.events.count(), 1)
        event_id = response.data['id']
        self.assertIsNotNone(event_id)
        event = Event.objects.filter(id=event_id).first()
        self.assertIsNotNone(event)
        self.assertEqual(event.admin_email, self.user.email)
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

    def test_create_event_with_different_user_than_admin(self):
        """Test creating a new event with a different user than the admin."""
        self.event.admin_email = 'another@email.com'
        self.event.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('api:event')
        data = {'token_code': self.token2.token_code}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_in_event_with_the_admin_user(self):
        """Test logging in an event with the same user."""
        self.event.admin_email = self.user.email
        self.event.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('api:event')
        data = {'token_code': self.token2.token_code}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    """***Start of the delete tests.***"""

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

    def test_get_event(self):
        """Test getting an event with a valid token."""
        self.user.events.add(self.event)
        self.user.save()
        url = reverse('api:event')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.expected_data)

    def test_get_event_unauthenticated(self):
        """Test getting an event without authentication."""
        url = reverse('api:event')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        self.user.delete()
        self.token.delete()
        self.token.token_code = None
        self.event_admin_user.delete()
        self.event.delete()
        self.group_event_admin.delete()
        self.permission.delete()
        self.client.logout()
        self.client.force_authenticate(user=None)
        if Event.objects.exists():
            Event.objects.all().delete()
