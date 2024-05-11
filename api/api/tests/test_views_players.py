import random
from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient
from api.models import Sumula, Event,  Token, Player
from users.models import User
import uuid
from ..utils import get_permissions, get_content_type
from django.contrib.auth.models import Group
from ..permissions import assign_permissions
from guardian.shortcuts import remove_perm, get_perms


class PlayersViewTest(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def remove_permissions(self, user, event):
        perms = get_perms(user, event)
        for perm in perms:
            remove_perm(perm, user, event)

    def generate_random_name(self):
        names = ['João', 'José', 'Pedro', 'Paulo', 'Lucas', 'Mário', 'Luiz']
        return names[random.randint(0, 6)]

    def setupUser(self):
        self.admin = User.objects.create(
            username='admin', email=f'{uuid.uuid4()}@gmail.com', first_name='Admin', last_name='Admin')
        self.user_staff_manager = User.objects.create(
            username='staff_manager', email=f'{uuid.uuid4()}@gmail.com', first_name='Staff', last_name='Manager')
        self.user_staff_member = User.objects.create(
            username='staff_member', email=f'{uuid.uuid4()}@gmail.com', first_name='Staff', last_name='Member')
        self.user = User.objects.create(
            username=self.create_unique_username(), email=f'{uuid.uuid4()}@gmail.com', first_name=self.generate_random_name(), last_name=self.generate_random_name())
        self.user2 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name=self.generate_random_name(), last_name=self.generate_random_name())

        self.user3 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name=self.generate_random_name(), last_name=self.generate_random_name())

        self.user4 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name=self.generate_random_name(), last_name=self.generate_random_name())

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpPlayers(self):
        self.player = Player.objects.create(
            user=self.user, event=self.event, registration_email=self.create_unique_email())
        self.player2 = Player.objects.create(
            user=self.user2, event=self.event, registration_email=self.create_unique_email())
        self.player3 = Player.objects.create(
            user=self.user3, event=self.event, registration_email=self.create_unique_email())
        self.player4 = Player.objects.create(
            user=self.user4, event=self.event, registration_email=self.create_unique_email())

    def setUpGroup(self):
        self.group_app_admin = Group.objects.create(name='app_admin')
        self.group_event_admin = Group.objects.create(name='event_admin')
        self.group_staff_manager = Group.objects.create(name='staff_manager')
        self.group_staff_member = Group.objects.create(name='staff_member')
        self.group_player = Group.objects.create(name='player')

    def setUpPermissions(self):
        assign_permissions(self.user_staff_manager,
                           self.group_staff_manager, self.event)
        assign_permissions(self.user_staff_member,
                           self.group_staff_member, self.event)
        assign_permissions(self.admin,
                           self.group_event_admin, self.event)
        assign_permissions(self.user, self.group_player, self.event)

    def setUp(self):
        self.setUpEvent()
        self.setupUser()
        self.setUpPlayers()
        self.setUpGroup()
        self.setUpPermissions()
        self.client = APIClient()
        self.url = f"{reverse('api:players')}?event_id={self.event.id}"

    def test_get_all_players(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

        expected_user_ids = [self.user.id,
                             self.user2.id, self.user3.id, self.user4.id]
        expected_registration_emails = [self.player.registration_email, self.player2.registration_email,
                                        self.player3.registration_email, self.player4.registration_email]

        returned_user_ids = [player['user']['id'] for player in response.data]
        returned_event_ids = [player['event'] for player in response.data]
        returned_registration_emails = [
            player['registration_email'] for player in response.data]

        self.assertCountEqual(returned_user_ids, expected_user_ids)
        self.assertTrue(
            all(event_id == self.event.id for event_id in returned_event_ids))
        self.assertCountEqual(returned_registration_emails,
                              expected_registration_emails)

    def test_get_all_players_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_players_without_event_id(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('api:players')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(response.data['errors'], 'event_id is required')

    def test_get_all_players_without_permission(self):
        self.remove_permissions(self.user, self.event)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_players_with_invalid_event_id(self):
        self.client.force_authenticate(user=self.admin)
        url = f"{reverse('api:players')}?event_id=100"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_players_withouth_any_player(self):
        self.client.force_authenticate(user=self.admin)
        Player.objects.all().delete()
        url = f"{reverse('api:players')}?event_id={self.event.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], 'Nenhum jogador encontrado!')

    def tearDown(self):
        User.objects.all().delete()
        Sumula.objects.all().delete()
        Event.objects.all().delete()
        Token.objects.all().delete()
        Player.objects.all().delete()
        Group.objects.all().delete()
        self.data = None


class GetCurrentPlayerViewTest(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def generate_random_name(self):
        names = ['João', 'José', 'Pedro', 'Paulo', 'Lucas', 'Mário', 'Luiz']
        return names[random.randint(0, 6)]

    def setupUser(self):
        self.user = User.objects.create(
            username=self.create_unique_username(), email=f'{uuid.uuid4()}@gmail.com',
            first_name=self.generate_random_name(), last_name=self.generate_random_name())
        self.user_staff_manager = User.objects.create(
            username='staff_manager', email=f'{uuid.uuid4()}@gmail.com')
        self.user_staff_member = User.objects.create(
            username='staff_member', email=f'{uuid.uuid4()}@gmail.com')
        self.admin = User.objects.create(
            username='admin', email=f'{uuid.uuid4()}@gmail.com')

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpPlayers(self):
        self.player = Player.objects.create(
            user=self.user, event=self.event, registration_email=self.create_unique_email())

    def setUpGroup(self):
        self.group_app_admin = Group.objects.create(name='app_admin')
        self.group_event_admin = Group.objects.create(name='event_admin')
        self.group_staff_manager = Group.objects.create(name='staff_manager')
        self.group_staff_member = Group.objects.create(name='staff_member')
        self.group_player = Group.objects.create(name='player')

    def setUpPermissions(self):
        assign_permissions(self.user_staff_manager,
                           self.group_staff_manager, self.event)
        assign_permissions(self.user_staff_member,
                           self.group_staff_member, self.event)
        assign_permissions(self.admin,
                           self.group_event_admin, self.event)
        assign_permissions(self.user, self.group_player, self.event)

    def setUp(self):
        self.setUpEvent()
        self.setupUser()
        self.setUpPlayers()
        self.setUpGroup()
        self.setUpPermissions()
        self.url = f"{reverse('api:player')}?event_id={self.event.id}"
        self.client = APIClient()

    def remove_permissions(self, user, event):
        perms = get_perms(user, event)
        for perm in perms:
            remove_perm(perm, user, event)

    def test_get_player(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.player.id,
            'total_score': self.player.total_score,
            'registration_email': self.player.registration_email,
            'event': self.event.id,
            'user': {
                'id': self.user.id,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name
            },
        })

    def test_get_player_without_event_id(self):
        self.client.force_authenticate(user=self.user)
        url = f"{reverse('api:player')}?event_id="
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errors': "['event_id é obrigatório!']"})

    def test_get_player_with_invalid_event_id(self):
        self.client.force_authenticate(user=self.user)
        url = f"{reverse('api:player')}?event_id=100"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errors': "['Evento não encontrado!']"})

    def test_get_player_without_permission(self):
        self.remove_permissions(self.user, self.event)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_player_unauthenticated(self):
        url = reverse('api:player')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_player_without_player_associated(self):
        self.client.force_authenticate(user=self.admin)
        Player.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data,  {'errors': 'Jogador não encontrado!'})

    def tearDown(self):
        User.objects.all().delete()
        Sumula.objects.all().delete()
        Event.objects.all().delete()
        Token.objects.all().delete()
        Player.objects.all().delete()
        Group.objects.all().delete()
        self.client = None
