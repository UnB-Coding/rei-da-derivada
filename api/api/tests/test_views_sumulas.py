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
from ..serializers import SumulaForPlayerSerializer, SumulaSerializer
from django.contrib.auth.models import Group
from guardian.shortcuts import remove_perm, assign_perm, get_perms


class BaseSumulaViewTest(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUpData(self):
        self.data_update = [
            {
                "id": self.sumula.id,
                "active": True,
                "description": 'Sala S4',
                "referee": [
                    {
                        "id": self.user_staff_manager.id,
                        "first_name": self.user_staff_manager.first_name,
                        "last_name": self.user_staff_manager.last_name
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
            ]
        }

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

    def setUpReferee(self, staff1: Staff, staff2: Staff, sumulas: list):
        for sumula in sumulas:
            sumula.referee.add(staff1)
            sumula.referee.add(staff2)

    def setUpPlayers(self):
        self.player = Player.objects.create(
            user=self.user_player1, event=self.event, registration_email=self.create_unique_email())
        self.player2 = Player.objects.create(
            user=self.user_player2, event=self.event, registration_email=self.create_unique_email())

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
            user=self.user_staff_manager, event=self.event)
        self.staff2 = Staff.objects.create(
            user=self.user_staff_member, event=self.event)


class SumulaViewTest(BaseSumulaViewTest):
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
            response.data['sumula_classificatoria'][0]['id'], self.sumula2.id)
        self.assertEqual(
            response.data['sumula_imortal'][0]['id'], self.sumula.id)
        self.assertEqual(
            response.data['sumula_imortal'][0]['referee'][0]['id'], self.staff1.id)
        # self.assertEqual(response.data[0]['sumula'])

    def test_get_active_sumulas(self):
        url = f"{reverse('api:sumula-ativas')}?event_id={self.event.id}"
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data['sumula_classificatoria'][0]['id'], self.sumula2.id)
        self.assertEqual(
            response.data['sumula_imortal'][0]['id'], self.sumula.id)
        self.assertEqual(
            response.data['sumula_imortal'][0]['referee'][0]['id'], self.staff1.id)

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
    def setUpSumula(self):
        self.sumula = SumulaImortal.objects.create(event=self.event)
        self.sumula2 = SumulaImortal.objects.create(event=self.event)
        self.sumula3 = SumulaImortal.objects.create(event=self.event)

    def setUpPlayerScore(self):
        self.player_score1 = PlayerScore.objects.create(
            player=self.player, sumula_imortal=self.sumula, event=self.event)
        self.player_score2 = PlayerScore.objects.create(
            player=self.player2, sumula_imortal=self.sumula, event=self.event)

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
        self.assertEqual(PlayerScore.objects.count(), 2)

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

    """*********Testes de GET*********"""

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

        self.data_update[0]['id'] = 100
        response = self.client.put(
            self.url_update, format='json', data=self.data_update)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], 'Sumula não encontrada!')

    def test_update_sumula_without_player_score_id(self):

        self.data_update[0]['players_score'][0].pop('id')
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(
            self.url_update, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'],
                         'Dados de pontuação inválidos!')

    def test_update_sumula_with_i_player_score_id_not_found(self):

        self.data_update[0]['players_score'][0]['id'] = 100
        self.client.force_authenticate(user=self.user_staff_manager)
        response = self.client.put(
            self.url_update, self.data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'],
                         'Dados de pontuação inválidos!')

    def tearDown(self):
        User.objects.all().delete()
        SumulaImortal.objects.all().delete()
        Event.objects.all().delete()
        PlayerScore.objects.all().delete()
        Token.objects.all().delete()
        Player.objects.all().delete()
        Group.objects.all().delete()
        self.remove_permissions()
        self.data_update = None


# class GetSumulaForPlayerTest(APITestCase):
#     def create_unique_email(self):
#         return f'{uuid.uuid4()}@gmail.com'

#     def create_unique_username(self):
#         return f'user_{uuid.uuid4().hex[:10]}'

#     def setUpData(self):
#         self.expected_data = SumulaForPlayerSerializer(
#             [self.sumula1, self.sumula2], many=True).data

#     def setUpSumula(self):
#         self.sumula1 = Sumula.objects.create(event=self.event)
#         self.sumula2 = Sumula.objects.create(event=self.event)

#     def setUpReferee(self, staff1: Staff, staff2: Staff, sumulas: list):
#         for sumula in sumulas:
#             sumula.referee.add(staff1)
#             sumula.referee.add(staff2)

#     def setUpPlayers(self):
#         self.player = Player.objects.create(
#             user=self.user, event=self.event, registration_email=self.create_unique_email())

#     def setUpPlayerScore(self):
#         self.player_score1 = PlayerScore.objects.create(
#             player=self.player, sumula=self.sumula1, event=self.event)
#         self.player_score2 = PlayerScore.objects.create(
#             player=self.player, sumula=self.sumula2, event=self.event)

#     def setUpGroup(self):
#         self.group_app_admin = Group.objects.create(name='app_admin')
#         self.group_player = Group.objects.create(name='player')

#     def setUpPermissions(self):
#         assign_permissions(self.user, self.group_player, self.event)

#     def setUpEvent(self):
#         self.token = Token.objects.create()
#         self.event = Event.objects.create(name='Evento 1', token=self.token)

#     def setUpUser(self):
#         self.user = User.objects.create(
#             username='test_user', email='example@email.com', first_name='Test', last_name='User')
#         self.user2 = User.objects.create(
#             username='test_user2', email='example2@email.com', first_name='Test2', last_name='User2')

#     def SetUpStaff(self):
#         self.staff1 = Staff.objects.create(
#             user=self.user2, event=self.event)
#         self.staff2 = Staff.objects.create(
#             user=self.user, event=self.event)

#     def setUp(self):
#         self.setUpEvent()
#         self.setUpUser()
#         self.setUpSumula()
#         self.setUpPlayers()
#         self.setUpPlayerScore()
#         self.setUpGroup()
#         self.SetUpStaff()
#         self.setUpReferee(self.staff2, self.staff1, [
#             self.sumula1, self.sumula2])
#         self.setUpPermissions()
#         self.setUpData()
#         self.client = APIClient()
#         self.url = f'{reverse("api:sumula-player")}?event_id={self.event.id}'

#     def test_get_sumulas_for_player(self):
#         data = {'event_id': self.event.id}
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(self.url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, self.expected_data)
#         self.assertEqual(len(response.data), 2)
#         self.assertEqual(response.data[0]['id'], self.sumula1.id)
#         self.assertEqual(response.data[1]['id'], self.sumula2.id)

#     def test_get_sumulas_for_player_unauthenticated(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_get_sumulas_for_player_invalid_event_id(self):
#         url = f'{reverse("api:sumula-player")}?event_id=10000'
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_get_sumulas_for_player_without_event_id(self):
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(reverse('api:sumula-player'))
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_get_sumulas_for_player_unauthorized(self):
#         self.client.force_authenticate(user=self.user2)
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def tearDown(self) -> None:
#         Event.objects.all().delete()
#         Sumula.objects.all().delete()
#         Player.objects.all().delete()
#         PlayerScore.objects.all().delete()
#         User.objects.all().delete()
#         Group.objects.all().delete()
#         Token.objects.all().delete()
