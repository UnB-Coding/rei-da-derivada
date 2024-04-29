from ast import Is
import email
from django.db import IntegrityError
from django.test import TestCase
from api.models import Token, Event
from users.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated


class TokenViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='testuser', email='example@email.com')

    def test_create_token(self):
        """Test creating a new token with a valid user."""
        url = reverse('api:token')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.count(), 1)

    def test_create_token_unauthenticated(self):
        """Test creating a new token without authentication."""
        url = reverse('api:token')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Token.objects.count(), 0)

    def tearDown(self):
        self.user.delete()
        self.client.logout()
        self.client.force_authenticate(user=None)
        if Token.objects.exists():
            Token.objects.all().delete()


class EventViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='testuser', email='test@email.com')
        self.token = Token.objects.create()

    def test_create_event(self):
        """Test creating a new event with a valid token."""
        url = reverse('api:event')
        data = {'token_code': self.token.token_code, 'name': 'New Event'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().name, 'New Event')

    def test_create_event_with_invalid_token(self):
        """Test creating a new event with an invalid token."""
        url = reverse('api:event')
        data = {'token_code': 'invalid_token', 'name': 'New Event'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Event.objects.count(), 0)

    def test_create_event_without_token(self):
        """Test creating a new event without a token."""
        url = reverse('api:event')
        data = {'name': 'New Event'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Event.objects.count(), 0)

    def test_create_event_unauthenticated(self):
        """Test creating a new event without authentication."""
        url = reverse('api:event')
        data = {'token_code': self.token.token_code, 'name': 'New Event'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Event.objects.count(), 0)

    def test_create_event_with_existing_token(self):
        """Test creating a new event with a token that already has an associated event."""
        self.token.mark_as_used()

        url = reverse('api:event')
        data = {'token_code': self.token.token_code, 'name': 'New Event'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Event.objects.count(), 0)

    def test_delete_event(self):
        """Test deleting an existing event with a valid token."""
        event = Event.objects.create(token=self.token, name='Test Event')
        url = reverse('api:event')
        data = {'token_code': self.token.token_code}
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Event.objects.count(), 0)

    def test_delete_event_with_invalid_token(self):
        """Test deleting an event with an invalid token."""
        url = reverse('api:event')
        data = {'token_code': 'invalid_token'}
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_event_without_associated_event(self):
        """Test deleting an event without an associated event."""
        url = reverse('api:event')
        data = {'token_code': self.token.token_code}
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        self.user.delete()
        self.token.delete()
        self.token.token_code = None
        self.client.logout()
        self.client.force_authenticate(user=None)
        if Event.objects.exists():
            Event.objects.all().delete()
