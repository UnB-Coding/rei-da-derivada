from django.forms import ValidationError
from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APIClient
from api.models import SumulaImortal, SumulaClassificatoria, Event, PlayerScore, Token, Player, Staff
from users.models import User
import uuid
from ..utils import get_permissions, get_content_type
from ..permissions import assign_permissions, filter_permissions
from ..serializers import SumulaForPlayerSerializer, SumulaImortalForPlayerSerializer, SumulaClassificatoriaForPlayerSerializer
from django.contrib.auth.models import Group
from guardian.shortcuts import remove_perm, assign_perm, get_perms


class BaseSumulaViewTest(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setupUser(self):
        self.user_staff_manager = User.objects.create(
            username=self.create_unique_username(), email=f'{uuid.uuid4()}@gmail.com', first_name='Manager', last_name='Staff')

        self.user_staff_member = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='Member', last_name='Staff')

        self.user_app_admin = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='Admin', last_name='App')
        self.user_player1 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='Player1', last_name='User')
        self.user_player2 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='Player2', last_name='User')
        self.user_player3 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email())
        self.user_player4 = User.objects.create(
            username='player4', email=self.create_unique_email())

    def setUpReferee(self, staff1: Staff, staff2: Staff, sumulas: list):
        for sumula in sumulas:
            sumula.referee.add(staff1)
            sumula.referee.add(staff2)

    def setUpPlayers(self):
        self.player = Player.objects.create(
            user=self.user_player1, event=self.event, registration_email=self.create_unique_email())
        self.player2 = Player.objects.create(
            user=self.user_player2, event=self.event, registration_email=self.create_unique_email())
        self.player3 = Player.objects.create(
            user=self.user_player3, event=self.event, registration_email=self.create_unique_email())
        self.player4 = Player.objects.create(
            user=self.user_player4, event=self.event, registration_email=self.create_unique_email())

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
        assign_permissions(self.user_app_admin,
                           self.group_event_admin, self.event)

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def remove_permissions(self):
        perm = get_perms(self.user_staff_manager, self.event)
        for p in perm:
            remove_perm(p, self.user_staff_manager, self.event)

    def SetUpStaff(self):
        self.staff1 = Staff.objects.create(
            user=self.user_staff_manager, event=self.event, registration_email=self.create_unique_email())
        self.staff2 = Staff.objects.create(
            user=self.user_staff_member, event=self.event, registration_email=self.create_unique_email())


class SumulaViewTest(BaseSumulaViewTest):
    def setUpData(self):
        self.data_update = [
            {
                "id": self.sumula.id,
                "active": True,
                "description": 'Sala S4',
                "referee": [
                    {
                        "id": self.staff1.id,
                    },
                    {
                        "id": self.user_staff_member.id,
                    }
                ],
                "name": "imortais 01",
                "players_score": [
                    {
                        "id": self.player_score1.id,
                        "points": 10,
                        "player": {
                            "id": self.player.id,
                            "total_score": 0,
                            "registration_email": self.player.registration_email,
                        }
                    },
                    {
                        "id": self.player_score2.id,
                        "points": 15,
                        "player": {
                            "id": self.player2.id,
                            "total_score": 0,
                            "registration_email": self.player2.registration_email,
                        }
                    }
                ]
            }
        ]
        self.data_post = {
            "name": "imortais 01",
            "players": [
                {
                    "id": self.player.id,
                    "total_score": self.player.total_score,
                },
                {
                    "id": self.player2.id,
                    "total_score": self.player2.total_score, }
            ],
            "referees": [
                {
                    "id": self.staff1.id,
                },

            ]
        }

    def setUpSumula(self):
        self.sumula = SumulaImortal.objects.create(event=self.event)
        self.sumula2 = SumulaClassificatoria.objects.create(event=self.event)
        self.sumula3 = SumulaImortal.objects.create(event=self.event)

    def setUpPlayerScore(self):
        self.player_score1 = PlayerScore.objects.create(
            player=self.player, sumula_imortal=self.sumula, event=self.event)
        self.player_score2 = PlayerScore.objects.create(
            player=self.player2, sumula_classificatoria=self.sumula2, event=self.event)

    def setUp(self):
        self.client = APIClient()
        self.setUpEvent()
        self.setUpSumula()
        self.setupUser()
        self.setUpGroup()
        self.SetUpStaff()
        self.setUpReferee(self.staff1, self.staff2, [
            self.sumula, self.sumula2, self.sumula3])
        self.setUpPlayers()
        self.setUpPlayerScore()
        self.setUpPermissions()
        self.url_post = f"{reverse('api:sumula')}?event_id={self.event.id}"
        self.url_get = f"{reverse('api:sumula')}?event_id={self.event.id}"
        self.url_update = f"{reverse('api:sumula')}?event_id={self.event.id}"
        self.setUpData()

    def test_get_sumulas(self):

        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.get(self.url_get)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data['sumulas_classificatoria'][0]['id'], self.sumula2.id)
        self.assertEqual(
            response.data['sumulas_imortal'][0]['id'], self.sumula.id)
        self.assertEqual(
            response.data['sumulas_imortal'][0]['referee'][0]['id'], self.staff1.id)
        # self.assertEqual(response.data[0]['sumula'])

    def test_get_active_sumulas(self):
        url = f"{reverse('api:sumula-ativas')}?event_id={self.event.id}"
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data['sumulas_classificatoria'][0]['id'], self.sumula2.id)
        self.assertEqual(
            response.data['sumulas_imortal'][0]['id'], self.sumula.id)
        self.assertEqual(
            response.data['sumulas_imortal'][0]['referee'][0]['id'], self.staff1.id)

    def test_get_finished_sumulas(self):
        self.sumula.active = False
        self.sumula.save()
        self.sumula2.active = False
        self.sumula2.save()
        url = f"{reverse('api:sumula-encerradas')}?event_id={self.event.id}"
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data['sumulas_classificatoria'][0]['id'], self.sumula2.id)
        self.assertEqual(
            response.data['sumulas_imortal'][0]['id'], self.sumula.id)
        self.assertEqual(
            response.data['sumulas_imortal'][0]['referee'][0]['id'], self.staff1.id)

    def test_get_sumulas_unauthenticated(self):
        response = self.client.get(self.url_get)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_sumulas_unauthorized(self):
        self.remove_permissions()
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.get(
            self.url_get)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SumulaImortalViewTest(BaseSumulaViewTest):
    def setUpData(self):
        self.data_update = {
            "id": self.sumula.id,
            "active": True,
            "description": 'Sala S4',
            "referee": [
                {
                    "id": self.staff1.id,
                },
                {
                    "id": self.user_staff_member.id,
                    "first_name": self.user_staff_member.first_name,
                    "last_name": self.user_staff_member.last_name
                }
            ],
            "name": "imortais 01",
            "players_score": [
                    {
                        "id": self.player_score1.id,
                        "points": 10,
                        "player": {
                            "id": self.player.id,
                            "total_score": 0,
                            "registration_email": self.player.registration_email,
                        }
                    },
                {
                        "id": self.player_score2.id,
                        "points": 15,
                        "player": {
                            "id": self.player2.id,
                            "total_score": 0,
                            "registration_email": self.player2.registration_email,
                        }
                        }
            ]
        }
        self.data_post = {
            "name": "imortais 01",
            "players": [
                {
                    "id": self.player.id,
                    "total_score": self.player.total_score,
                },
                {
                    "id": self.player2.id,
                    "total_score": self.player2.total_score, },
                {
                    "id": self.player3.id,
                    "total_score": self.player3.total_score, },
                {
                    "id": self.player4.id,
                    "total_score": self.player4.total_score,
                }
            ],
            "referees": [
                {
                    "id": self.staff1.id,
                },

            ]
        }

    def setUpSumula(self):
        self.sumula = SumulaImortal.objects.create(event=self.event)
        self.sumula2 = SumulaImortal.objects.create(event=self.event)
        self.sumula3 = SumulaImortal.objects.create(event=self.event)

    def setUpPlayerScore(self):
        self.player_score1 = PlayerScore.objects.create(
            player=self.player, sumula_imortal=self.sumula, event=self.event)
        self.player_score2 = PlayerScore.objects.create(
            player=self.player2, sumula_imortal=self.sumula, event=self.event)
        self.player_score3 = PlayerScore.objects.create(
            player=self.player3, sumula_imortal=self.sumula2, event=self.event)
        self.player_score4 = PlayerScore.objects.create(
            player=self.player4, sumula_imortal=self.sumula2, event=self.event)

    def setUp(self):
        self.client = APIClient()
        self.setUpEvent()
        self.setUpSumula()
        self.setupUser()
        self.setUpGroup()
        self.SetUpStaff()
        self.setUpReferee(self.staff1, self.staff2, [
            self.sumula, self.sumula2, self.sumula3])
        self.setUpPlayers()
        self.setUpPlayerScore()
        self.setUpPermissions()
        self.url_post = f"{reverse('api:sumula-imortal')}?event_id={self.event.id}"
        self.url_get = f"{reverse('api:sumula-imortal')}?event_id={self.event.id}"
        self.url_update = f"{reverse('api:sumula-imortal')}?event_id={self.event.id}"
        self.setUpData()

    """*********Testes de Create*********"""

    def test_create_sumula(self):
        PlayerScore.objects.all().delete()
        self.assertFalse(PlayerScore.objects.exists())
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.post(
            self.url_post, self.data_post, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SumulaImortal.objects.count(), 4)
        self.assertEqual(PlayerScore.objects.count(), 4)
        self.assertIsNotNone(SumulaImortal.objects.filter(
            name='Imortais 01').first())
        sumula_id = response.data['id']
        sumula = SumulaImortal.objects.get(id=sumula_id)
        self.assertEqual(sumula.referee.count(), 1)

    def test_create_sumula_without_referee(self):
        self.data_post['referees'] = []
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.post(
            self.url_post, self.data_post, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sumula_id = response.data['id']
        sumula = SumulaImortal.objects.get(id=sumula_id)
        self.assertEqual(sumula.referee.count(), 0)

    def test_create_sumula_unauthenticated(self):
        response = self.client.post(
            self.url_post, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_sumula_invalid_data(self):
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.post(self.url_post, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sumula_invalid_data2(self):
        self.client.force_authenticate(user=self.user_staff_manager)

        self.client.post(self.url_post, {'players': []}, format='json')
        response = self.client.post(
            self.url_post, {'players': [{}]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sumula_unauthorized(self):
        self.remove_permissions()

        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.post(
            self.url_post, self.data_post, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    """*********Testes de update*********"""

    def test_update_sumula(self):

        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(
            self.url_update, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sumula.refresh_from_db()
        referees = self.sumula.referee.all()
        scores = self.sumula.scores.all()
        self.assertIsNotNone(self.sumula)
        self.assertEqual(len(referees), 2)
        self.assertEqual(len(scores), 2)
        self.assertEqual(self.sumula.name, 'Imortais 01')
        self.assertEqual(self.sumula.referee.count(), 2)
        self.assertEqual(self.sumula.scores.count(), 2)
        self.assertFalse(SumulaImortal.objects.get(id=self.sumula.id).active)
        self.assertEqual(self.sumula.description, "Sala S4")
        for referee in referees:
            self.assertIn(
                referee, [self.staff1, self.staff2])

        for score in scores:
            self.assertIn(score.player, [self.player, self.player2])
            self.assertIn(score.points, [10, 15])
            self.assertEqual(score.player.total_score, score.points)

    def test_update_sumula_unauthenticated(self):

        response = self.client.put(
            self.url_update, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_sumula_invalid_data(self):

        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(self.url_update, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_sumula_unauthorized(self):
        self.remove_permissions()
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(
            self.url_update, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_sumula_not_found(self):
        self.client.force_authenticate(user=self.user_staff_manager)

        self.data_update['id'] = 100
        response = self.client.put(
            self.url_update, format='json', data=self.data_update)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], 'Sumula não encontrada!')

    def test_update_sumula_without_player_score_id(self):

        self.data_update['players_score'][0].pop('id')
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(
            self.url_update, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_sumula_with_i_player_score_id_not_found(self):

        self.data_update['players_score'][0]['id'] = 100
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(
            self.url_update, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        User.objects.all().delete()
        SumulaImortal.objects.all().delete()
        Event.objects.all().delete()
        PlayerScore.objects.all().delete()
        Token.objects.all().delete()
        Player.objects.all().delete()
        Group.objects.all().delete()
        self.remove_permissions()
        self.data_post = None


class SumulaClassificatoriaViewTest(BaseSumulaViewTest):
    def setUpData(self):
        self.data_update = {
            "id": self.sumula.id,
            "active": True,
            "description": 'Sala S4',
            "referee": [
                {
                    "id": self.staff1.id,
                },
            ],
            "name": "imortais 01",
            "players_score": [
                    {
                        "id": self.player_score1.id,
                        "points": 10,
                        "player": {
                            "id": self.player.id,
                            "total_score": 0,
                            "registration_email": self.player.registration_email,
                        }
                    },
                {
                        "id": self.player_score2.id,
                        "points": 15,
                        "player": {
                            "id": self.player2.id,
                            "total_score": 0,
                            "registration_email": self.player2.registration_email,
                        }
                        }
            ]
        }
        self.data_post = {
            "name": "imortais 01",
            "players": [
                {
                    "id": self.player.id,
                    "total_score": self.player.total_score,
                },
                {
                    "id": self.player2.id,
                    "total_score": self.player2.total_score, },
                {
                    "id": self.player3.id,
                    "total_score": self.player3.total_score, },
                {
                    "id": self.player4.id,
                    "total_score": self.player4.total_score,
                }
            ],
            "referees": [
                {
                    "id": self.staff1.id,
                },

            ]
        }

    def setUpSumula(self):
        self.sumula = SumulaClassificatoria.objects.create(event=self.event)
        self.sumula2 = SumulaClassificatoria.objects.create(event=self.event)
        self.sumula3 = SumulaClassificatoria.objects.create(event=self.event)

    def setUpPlayerScore(self):
        self.player_score1 = PlayerScore.objects.create(
            player=self.player, sumula_classificatoria=self.sumula, event=self.event)
        self.player_score2 = PlayerScore.objects.create(
            player=self.player2, sumula_classificatoria=self.sumula, event=self.event)
        self.player_score3 = PlayerScore.objects.create(
            player=self.player3, sumula_classificatoria=self.sumula2, event=self.event)
        self.player_score4 = PlayerScore.objects.create(
            player=self.player4, sumula_classificatoria=self.sumula2, event=self.event)

    def setUp(self):
        self.client = APIClient()
        self.setUpEvent()
        self.setUpSumula()
        self.setupUser()
        self.setUpGroup()
        self.SetUpStaff()
        self.setUpReferee(self.staff1, self.staff2, [
            self.sumula, self.sumula2, self.sumula3])
        self.setUpPlayers()
        self.setUpPlayerScore()
        self.setUpPermissions()
        self.url_post = f"{reverse('api:sumula-classificatoria')}?event_id={self.event.id}"
        self.url_get = f"{reverse('api:sumula-classificatoria')}?event_id={self.event.id}"
        self.url_update = f"{reverse('api:sumula-classificatoria')}?event_id={self.event.id}"
        self.setUpData()

    """*********Testes de Create*********"""

    def test_create_sumula(self):
        PlayerScore.objects.all().delete()
        SumulaClassificatoria.objects.all().delete()
        self.assertFalse(PlayerScore.objects.exists())
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.post(
            self.url_post, self.data_post, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SumulaClassificatoria.objects.count(), 1)
        self.assertEqual(PlayerScore.objects.count(), 4)
        sumula = SumulaClassificatoria.objects.get(id=response.data['id'])
        self.assertEqual(sumula.referee.count(), 1)

    def test_create_sumula_unauthenticated(self):
        response = self.client.post(
            self.url_post, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_sumula_invalid_data(self):
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.post(self.url_post, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sumula_invalid_data2(self):
        self.client.force_authenticate(user=self.user_staff_manager)

        self.client.post(self.url_post, {'players': []}, format='json')
        response = self.client.post(
            self.url_post, {'players': [{}]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sumula_unauthorized(self):
        self.remove_permissions()

        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.post(
            self.url_post, self.data_post, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    """*********Testes de update*********"""

    def test_update_sumula(self):

        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(
            self.url_update, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sumula.refresh_from_db()
        referees = self.sumula.referee.all()
        scores = self.sumula.scores.all()
        self.assertIsNotNone(self.sumula)
        self.assertEqual(len(referees), 2)
        self.assertEqual(len(scores), 2)
        self.assertEqual(self.sumula.name, 'imortais 01')
        self.assertEqual(self.sumula.referee.count(), 2)
        self.assertEqual(self.sumula.scores.count(), 2)
        self.assertFalse(SumulaClassificatoria.objects.get(
            id=self.sumula.id).active)
        self.assertEqual(self.sumula.description, "Sala S4")
        for referee in referees:
            self.assertIn(
                referee, [self.staff1, self.staff2])

        for score in scores:
            self.assertIn(score.player, [self.player, self.player2])
            self.assertIn(score.points, [10, 15])
            self.assertEqual(score.player.total_score, score.points)

    def test_update_sumula_unauthenticated(self):

        response = self.client.put(
            self.url_update, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_sumula_invalid_data(self):

        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(self.url_update, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_sumula_unauthorized(self):
        self.remove_permissions()
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(
            self.url_update, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_sumula_not_found(self):
        self.client.force_authenticate(user=self.user_staff_manager)

        self.data_update['id'] = 100
        response = self.client.put(
            self.url_update, format='json', data=self.data_update)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], 'Sumula não encontrada!')

    def test_update_sumula_without_player_score_id(self):

        self.data_update['players_score'][0].pop('id')
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(
            self.url_update, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_sumula_with_i_player_score_id_not_found(self):

        self.data_update['players_score'][0]['id'] = 100
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(
            self.url_update, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        User.objects.all().delete()
        SumulaClassificatoria.objects.all().delete()
        Event.objects.all().delete()
        PlayerScore.objects.all().delete()
        Token.objects.all().delete()
        Player.objects.all().delete()
        Group.objects.all().delete()
        self.remove_permissions()
        self.data_update = None
        self.data_post = None


class GetSumulaForPlayerTest(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUpData(self):
        self.expected_data_classificatoria = SumulaClassificatoriaForPlayerSerializer(
            [self.sumula_classificatoria1, self.sumula_classificatoria2], many=True).data
        self.player.is_imortal = True
        self.player.save()
        self.expected_data_imortal = SumulaImortalForPlayerSerializer(
            [self.sumula_imortal1, self.sumula_imortal2], many=True).data
        self.player.is_imortal = False
        self.player.save()

    def setUpSumula(self):
        self.sumula_imortal1 = SumulaImortal.objects.create(
            event=self.event, name='Imortais 01')
        self.sumula_imortal2 = SumulaImortal.objects.create(
            event=self.event, name='Imortais 02')
        self.sumula_classificatoria1 = SumulaClassificatoria.objects.create(
            event=self.event, name='Chave 01')
        self.sumula_classificatoria2 = SumulaClassificatoria.objects.create(
            event=self.event, name='Chave 02')

    def setUpReferee(self, staff1: Staff, staff2: Staff, sumulas: list):
        for sumula in sumulas:
            sumula.referee.add(staff1)
            sumula.referee.add(staff2)

    def setUpPlayers(self):
        self.player = Player.objects.create(
            user=self.user, event=self.event, registration_email=self.create_unique_email())

    def setUpPlayerScore(self):
        self.player_score1_imortal = PlayerScore.objects.create(
            player=self.player, sumula_imortal=self.sumula_imortal1, event=self.event)
        self.player_score2_imortal = PlayerScore.objects.create(
            player=self.player, sumula_imortal=self.sumula_imortal2, event=self.event)
        self.player_score1_classificatoria = PlayerScore.objects.create(
            player=self.player, sumula_classificatoria=self.sumula_classificatoria1, event=self.event)
        self.player_score2_classificatoria = PlayerScore.objects.create(
            player=self.player, sumula_classificatoria=self.sumula_classificatoria2, event=self.event)

    def setUpGroup(self):
        self.group_app_admin = Group.objects.create(name='app_admin')
        self.group_player = Group.objects.create(name='player')

    def setUpPermissions(self):
        assign_permissions(self.user, self.group_player, self.event)

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpUser(self):
        self.user = User.objects.create(
            username='test_user', email='example@email.com', first_name='Test', last_name='User')
        self.user2 = User.objects.create(
            username='test_user2', email='example2@email.com', first_name='Test2', last_name='User2')

    def SetUpStaff(self):
        self.staff1 = Staff.objects.create(
            user=self.user2, event=self.event, registration_email=self.create_unique_email())
        self.staff2 = Staff.objects.create(
            user=self.user, event=self.event, registration_email=self.create_unique_email())

    def setUp(self):
        self.setUpEvent()
        self.setUpUser()
        self.setUpSumula()
        self.setUpPlayers()
        self.setUpPlayerScore()
        self.setUpGroup()
        self.SetUpStaff()
        self.setUpReferee(self.staff2, self.staff1, [
                          self.sumula_imortal1, self.sumula_imortal2, self.sumula_classificatoria1, self.sumula_classificatoria2])
        self.setUpPermissions()
        self.setUpData()
        self.client = APIClient()
        self.url = f'{reverse("api:sumula-player")}?event_id={self.event.id}'

    def test_get_sumulas_for_player_not_imortal(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.expected_data_classificatoria)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'],
                         self.sumula_classificatoria1.id)
        self.assertEqual(response.data[1]['id'],
                         self.sumula_classificatoria2.id)

    def test_get_sumulas_for_player_imortal(self):
        self.player.is_imortal = True
        self.player.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.expected_data_imortal)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'],
                         self.sumula_imortal1.id)
        self.assertEqual(response.data[1]['id'],
                         self.sumula_imortal2.id)

    def test_get_sumulas_for_player_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_sumulas_for_player_invalid_event_id(self):
        url = f'{reverse("api:sumula-player")}?event_id=10000'
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_sumulas_for_player_without_event_id(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:sumula-player'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_sumulas_for_player_unauthorized(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_sumulas_without_existent_player(self):
        self.player.delete()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self) -> None:
        Event.objects.all().delete()
        SumulaImortal.objects.all().delete()
        SumulaClassificatoria.objects.all().delete()
        Player.objects.all().delete()
        PlayerScore.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()
        Token.objects.all().delete()


class AddRefereeToSumulaTestCase(BaseSumulaViewTest):
    def setUpSumula(self):
        self.sumula_imortal1 = SumulaImortal.objects.create(event=self.event)
        self.sumula_classficatoria1 = SumulaClassificatoria.objects.create(
            event=self.event)
        self.sumula_imortal2 = SumulaImortal.objects.create(event=self.event)

    def setUp(self):
        self.client = APIClient()
        self.setUpEvent()
        self.setupUser()
        self.setUpGroup()
        self.SetUpStaff()
        self.setUpSumula()
        self.setUpPermissions()
        self.url = f"{reverse('api:sumula-add-referee')}?event_id={self.event.id}"
        self.data = {
            "sumula_id": self.sumula_imortal1.id,
            "is_imortal": True
        }

    def test_add_referee_to_sumula_all_correct(self):
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sumula_imortal1.refresh_from_db()
        self.assertEqual(self.sumula_imortal1.referee.count(), 1)
        self.assertIn(self.staff1, self.sumula_imortal1.referee.all())

    def test_add_referee_to_sumula_unauthenticated(self):
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_referee_to_sumula_with_unauthorized_user(self):
        self.remove_permissions()
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_referee_to_sumula_with_no_staff_object_associated(self):
        Staff.objects.all().delete()
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_referee_to_sumula_without_sumula_id(self):
        self.data.pop('sumula_id')
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_refere_to_sumula_without_is_imortal(self):
        self.data.pop('is_imortal')
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self) -> None:
        Event.objects.all().delete()
        SumulaImortal.objects.all().delete()
        SumulaClassificatoria.objects.all().delete()
        Player.objects.all().delete()
        PlayerScore.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()
        Token.objects.all().delete()
        Staff.objects.all().delete()
