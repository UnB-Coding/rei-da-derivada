from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from api.models import Sumula, Event, PlayerScore, Token
from users.models import User
from rest_framework.test import force_authenticate
from ..utils import get_permissions, get_content_type
from django.contrib.auth.models import Group


class SumulaViewTest(APITestCase):
    def setUp(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)
        self.sumula = Sumula.objects.create(event=self.event)
        self.user = User.objects.create(username='user1')
        self.player_score = PlayerScore.objects.create(
            user=self.user, sumula=self.sumula, points=0, event=self.event)
        self.sumula_content_type = get_content_type(Sumula)
        self.permission = get_permissions(self.sumula_content_type)
        self.group = Group.objects.create(name='Grupo_teste')
        self.group.permissions.set(self.permission)
        self.user.groups.add(self.group)
        self.url = f"{reverse('api:sumula')}?event_id={self.event.id}"

    def test_create_sumula(self):

        data = {
            'players': [{'user_id': self.user.id}]
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sumula.objects.count(), 2)
        self.assertEqual(PlayerScore.objects.count(), 2)

    def test_get_sumulas(self):

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {'event_id': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_active_sumulas(self):
        url = reverse('api:sumula-ativas')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {'event_id': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_sumula(self):
        url = f"{reverse('api:sumula')}?sumula_id={self.sumula.id}"
        data = {'sumula_id': self.sumula.id}
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Sumula.objects.get(id=self.sumula.id).active)

    def test_get_sumulas_unauthenticated(self):
        response = self.client.get(self.url, {'event_id': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_sumula_unauthenticated(self):
        data = {
            'players': [{'user_id': self.user.id}]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_sumula_unauthenticated(self):
        url = f"{reverse('api:sumula')}?sumula_id={self.sumula.id}"
        data = {'sumula_id': self.sumula.id}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_sumula_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sumula_invalid_data2(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'players': [{}]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_sumula_invalid_data(self):
        url = f"{reverse('api:sumula')}?sumula_id={self.sumula.id}"
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sumula_unauthorized(self):
        self.user.groups.remove(self.group)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_sumula_unauthorized(self):
        self.user.groups.remove(self.group)
        url = f"{reverse('api:sumula')}?sumula_id={self.sumula.id}"
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_sumulas_unauthorized(self):
        self.user.groups.remove(self.group)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {'event_id': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_sumula_not_found(self):
        url = f"{reverse('api:sumula')}?sumula_id=0"
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


def tearDown(self):
    self.event.delete()
    self.sumula.delete()
    self.user.delete()
    self.player_score.delete()
    self.client.logout()
    self.group.delete()
    self.permission.delete()
    self.sumula_content_type.delete()
