from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase
from api.models import Player, Token, Event, SumulaImortal, SumulaClassificatoria, PlayerScore, Staff, TOKEN_LENGTH
from users.models import User
from unittest import TestCase
import uuid
# Create your tests here.


class TokenTest(TestCase):

    def setUp(self) -> None:
        self.token = Token.objects.create()
        self.token.save()

    def test_generate_token(self):
        """Testa a geração de um token"""
        self.token.generate_token()
        self.assertTrue(len(self.token.token_code) == TOKEN_LENGTH)

    def test_create_valid_token(self):
        """Testa a criacao de um token e sua validade"""

        self.assertIsNotNone(self.token)
        self.assertIsNotNone(self.token.token_code)

    def test_cannot_create_duplicate_token(self):
        """Testa que não é possível criar um token com o mesmo código"""
        with self.assertRaises(IntegrityError):
            Token.objects.create(token_code=self.token.token_code)

    def test_is_used(self):
        """Testa a atribuição de um token como não usado após a criação"""

        self.assertFalse(self.token.is_used())

    def test_used_token(self):
        """Testa a marcação de um token como usado"""

        self.assertFalse(self.token.is_used())
        self.token.mark_as_used()
        self.assertTrue(self.token.is_used())

    def test_save_token_without_code(self):
        """Testa a chamada do método generate_token dentro do metodo save de um token sem código"""
        token = Token()
        token.save()
        self.assertIsNotNone(token.token_code)
        self.assertTrue(len(token.token_code) == TOKEN_LENGTH)

    def test_delete_token(self):
        """Testa a deleção de um token"""
        self.token.delete()
        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(token_code=self.token.token_code)

    def test_can_not_edit_token_code(self):
        """Testa que não é possível editar o código de um token"""
        self.token.token_code = "ABC123"

    def test_token_str(self):
        """Testa a representação de um token"""
        self.assertEqual(self.token.__str__(), (self.token.token_code))

    def tearDown(self) -> None:
        if Token.objects.all().count() > 0:
            Token.objects.all().delete()

    @classmethod
    def tearDownClass(cls) -> None:
        if Token.objects.all().count() > 0:
            Token.objects.all().delete()
        return super().tearDownClass()


class EventTest(TestCase):
    def setUp(self):
        self.token = Token.objects.create()
        self.token.save()

    def test_create_event(self):
        """Testa a criação de um evento"""
        event = Event.objects.create(name='Evento 1', token=self.token)
        self.assertIsNotNone(event)
        self.assertEqual(event.name, 'Evento 1')
        self.assertEqual(event.token, self.token)
        self.assertEqual(event.active, True)
        self.assertIsNotNone(event.join_token)
        self.assertTrue(len(event.join_token) == TOKEN_LENGTH)

    def test_create_event_without_anything(self):
        """Testa a criação de um evento sem nada"""
        with self.assertRaises(IntegrityError):
            Event.objects.create()

    def test_create_event_without_name(self):
        """Testa a criação de um evento sem nome"""
        event = Event.objects.create(token=self.token)
        self.assertIsNotNone(event)
        self.assertEqual(event.name, '')

    def test_create_event_without_token(self):
        """Testa a criação de um evento sem token"""
        with self.assertRaises(IntegrityError):
            Event.objects.create(name='Evento 1')

    def test_edit_event_name(self):
        """Testa a edição do nome de um evento"""
        event = Event.objects.create(name='Evento 1', token=self.token)
        event.name = 'Evento 2'
        event.save()
        self.assertEqual(event.name, 'Evento 2')

    # def test_delete_token_with_event(self):
        """Testa a deleção de um token com eventos associados"""
        """ event = Event.objects.create(name='Evento 1', token=self.token)
        self.token.delete()
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(name='Evento 1')
 """

    def test_event_str(self):
        """Testa a representação de um evento"""
        event = Event.objects.create(name='Evento 1', token=self.token)
        self.assertEqual(event.__str__(), "Evento 1")

    def test_event_token(self):
        """Testa a representação do token de um evento"""
        event = Event.objects.create(name='Evento 1', token=self.token)
        self.assertEqual(event.__token__(), self.token.token_code)

    def tearDown(self) -> None:
        self.token.delete()
        if Event.objects.all().count() > 0:
            Event.objects.all().delete()


class SumulaImortalTest(TestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUp(self):
        self.token = Token.objects.create()
        self.user = User.objects.create(
            email=self.create_unique_email(), username=self.create_unique_username())
        self.user_2 = User.objects.create(
            email=self.create_unique_email(), username=self.create_unique_username())
        self.event = Event.objects.create(name='Evento 1', token=self.token)
        self.sumula = SumulaImortal.objects.create(
            name='Sumula 1', event=self.event)
        self.staff1 = Staff.objects.create(
            user=self.user, event=self.event, registration_email=self.create_unique_email())
        self.staff2 = Staff.objects.create(
            user=self.user_2, event=self.event, registration_email=self.create_unique_email())

    def test_create_sumula_without_referee(self):
        """Testa a criação de uma sumula"""
        sumula = SumulaImortal.objects.create(
            name='Sumula 2', event=self.event)
        self.assertEqual(sumula.name, 'Sumula 2')
        self.assertEqual(sumula.event, self.event)

    def test_add_referee_to_sumula(self):
        """Testa a criação de uma sumula com árbitros"""
        sumula = SumulaImortal.objects.create(
            name='Sumula 1', event=self.event)
        sumula.referee.add(self.staff1)
        sumula.referee.add(self.staff2)
        self.assertIn(self.staff1, sumula.referee.all())
        self.assertIn(self.staff2, sumula.referee.all())

    def test_remove_one_referee_from_sumula(self):
        """Testa a remoção de um árbitro de uma sumula"""
        self.sumula.referee.add(self.staff1)
        self.sumula.save()
        self.sumula.referee.remove(self.staff1)
        self.sumula.save()
        self.sumula.refresh_from_db()
        self.assertNotIn(self.staff1, self.sumula.referee.all())

    def test_remove_all_referees_from_sumula(self):
        """Testa a remoção de todos os árbitros de uma sumula"""
        self.sumula.referee.add(self.staff1)
        self.sumula.referee.add(self.staff2)
        self.sumula.referee.clear()
        self.assertEqual(self.sumula.referee.count(), 0)

    def test_sumula_str(self):
        """Testa a representação de uma sumula"""
        self.assertEqual(self.sumula.__str__(), 'Sumula 1')

    def tearDown(self) -> None:
        self.token.delete()
        self.user.delete()
        self.user_2.delete()
        self.event.delete()
        self.sumula.delete()
        return super().tearDown()

    @classmethod
    def tearDownClass(cls) -> None:
        if User.objects.all().count() > 0:
            User.objects.all().delete()
        return super().tearDownClass()


class SumulaClassificatoriaTest(TestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUp(self):
        self.token = Token.objects.create()
        self.user = User.objects.create(
            email=self.create_unique_email(), username=self.create_unique_username())
        self.user_2 = User.objects.create(
            email=self.create_unique_email(), username=self.create_unique_username())
        self.event = Event.objects.create(name='Evento 1', token=self.token)
        self.sumula = SumulaClassificatoria.objects.create(
            name='Sumula 1', event=self.event)
        self.staff1 = Staff.objects.create(
            user=self.user, event=self.event, registration_email=self.create_unique_email())
        self.staff2 = Staff.objects.create(
            user=self.user_2, event=self.event, registration_email=self.create_unique_email())

    def test_create_sumula_without_referee(self):
        """Testa a criação de uma sumula"""
        sumula = SumulaClassificatoria.objects.create(
            name='Sumula 2', event=self.event)
        self.assertEqual(sumula.name, 'Sumula 2')
        self.assertEqual(sumula.event, self.event)

    def test_add_referee_to_sumula(self):
        """Testa a criação de uma sumula com árbitros"""
        sumula = SumulaClassificatoria.objects.create(
            name='Sumula 1', event=self.event)
        sumula.referee.add(self.staff1)
        sumula.referee.add(self.staff2)
        self.assertIn(self.staff1, sumula.referee.all())
        self.assertIn(self.staff2, sumula.referee.all())

    def test_remove_one_referee_from_sumula(self):
        """Testa a remoção de um árbitro de uma sumula"""
        self.sumula.referee.add(self.staff1)
        self.sumula.save()
        self.sumula.referee.remove(self.staff1)
        self.sumula.save()
        self.sumula.refresh_from_db()
        self.assertNotIn(self.staff1, self.sumula.referee.all())

    def test_remove_all_referees_from_sumula(self):
        """Testa a remoção de todos os árbitros de uma sumula"""
        self.sumula.referee.add(self.staff1)
        self.sumula.referee.add(self.staff2)
        self.sumula.referee.clear()
        self.assertEqual(self.sumula.referee.count(), 0)

    def test_sumula_str(self):
        """Testa a representação de uma sumula"""
        self.assertEqual(self.sumula.__str__(), 'Sumula 1')

    def tearDown(self) -> None:
        self.token.delete()
        self.user.delete()
        self.user_2.delete()
        self.event.delete()
        self.sumula.delete()
        return super().tearDown()

    @classmethod
    def tearDownClass(cls) -> None:
        if User.objects.all().count() > 0:
            User.objects.all().delete()
        return super().tearDownClass()


class PlayerScoreTest(TestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUp(self):
        self.token = Token.objects.create()
        self.user = User.objects.create(
            email=self.create_unique_email(), username=self.create_unique_username(), first_name='Test', last_name='User')
        self.event = Event.objects.create(name='Evento 1', token=self.token)
        self.sumulaImortal = SumulaImortal.objects.create(
            name='Sumula Imortal', event=self.event)
        self.sumulaClassificatoria = SumulaClassificatoria.objects.create(
            name='Sumula Classificatoria', event=self.event)
        self.player = Player.objects.create(
            user=self.user, event=self.event, registration_email='email@teste.com')
        self.player_scoreImortal = PlayerScore.objects.create(
            player=self.player, event=self.event, sumula_imortal=self.sumulaImortal, points=0)
        self.player_scoreClassificatoria = PlayerScore.objects.create(
            player=self.player, event=self.event, sumula_classificatoria=self.sumulaClassificatoria, points=0)

    def test_create_empty_player_score(self):
        """Testa a criação de uma pontuação de jogador"""
        self.assertEqual(self.player_scoreImortal.player, self.player)
        self.assertEqual(self.player_scoreImortal.event, self.event)
        self.assertEqual(
            self.player_scoreImortal.sumula_imortal, self.sumulaImortal)
        self.assertEqual(self.player_scoreImortal.points, 0)

        self.assertEqual(self.player_scoreClassificatoria.player, self.player)
        self.assertEqual(self.player_scoreClassificatoria.event, self.event)
        self.assertEqual(
            self.player_scoreClassificatoria.sumula_classificatoria, self.sumulaClassificatoria)
        self.assertEqual(self.player_scoreImortal.points, 0)

    def test_edit_points_to_player_score(self):
        self.player_scoreImortal.points = 10
        self.player_scoreImortal.save()
        self.assertEqual(self.player_scoreImortal.points, 10)
        self.assertEqual(str(self.player_scoreImortal), f'{self.player} - 10')

    def test_update_total_score_within_save_method(self):
        self.assertEqual(self.player.total_score, 0)
        self.player_scoreImortal.points = 10
        self.player_scoreImortal.save()

        self.assertEqual(self.player.total_score, 10)

    # def test_create_player_score_without_player(self):
    #     """Testa a criação de uma pontuação de jogador sem usuário"""
    #     with self.assertRaises(IntegrityError):
    #         PlayerScore.objects.create(
    #             event=self.event, sumula_imortal=self.sumulaImortal, points=0)

    # def test_create_player_score_without_event(self):
    #     """Testa a criação de uma pontuação de jogador sem evento"""
    #     with self.assertRaises(IntegrityError):
    #         PlayerScore.objects.create(
    #             player=self.player, sumula_imortal=self.sumulaImortal)

    def test_create_player_score_without_sumula(self):
        """Testa a criação de uma pontuação de jogador sem sumula"""
        with self.assertRaises(ValidationError):
            PlayerScore.objects.create(player=self.player, event=self.event)

    def test_create_player_score_with_sumula_imortal_and_sumula_classificatoria(self):
        """Testa a criação de uma pontuação de jogador com sumula imortal e sumula classificatoria"""
        with self.assertRaises(ValidationError):
            PlayerScore.objects.create(player=self.player, event=self.event,
                                       sumula_imortal=self.sumulaImortal, sumula_classificatoria=self.sumulaClassificatoria)

    def test_create_player_score_without_points(self):
        """Testa a criação de uma pontuação de jogador sem pontos"""
        player_score = PlayerScore.objects.create(
            player=self.player, event=self.event, sumula_imortal=self.sumulaImortal)
        self.assertEqual(player_score.points, 0)

    def test_create_player_score_with_negative_points(self):
        """Testa a criação de uma pontuação de jogador com pontos negativos"""
        with self.assertRaises(IntegrityError):
            PlayerScore.objects.create(
                player=self.player, event=self.event, sumula_imortal=self.sumulaImortal, points=-10)

    def test_delete_player_score(self):
        """Testa a deleção de uma pontuação de jogador"""
        self.player_scoreImortal.delete()
        with self.assertRaises(PlayerScore.DoesNotExist):
            PlayerScore.objects.get(
                player=self.player, event=self.event, sumula_imortal=self.sumulaImortal)

    def test_player_score_str(self):
        """Testa a representação de uma pontuação de jogador"""
        self.assertEqual(str(self.player_scoreImortal), f'{self.player} - 0')

    def test_delete_and_update_total_score(self):
        self.assertEqual(self.player.total_score, 0)
        self.player_scoreImortal.points = 10
        self.player_scoreImortal.save()
        self.player.refresh_from_db()
        self.assertEqual(self.player.total_score, 10)
        self.player_scoreImortal.delete()
        self.player.refresh_from_db()
        self.assertEqual(self.player.total_score, 0)

    def tearDown(self):
        Event.objects.all().delete()
        Token.objects.all().delete()
        User.objects.all().delete()
        SumulaImortal.objects.all().delete()
        SumulaClassificatoria.objects.all().delete()
        PlayerScore.objects.all().delete()
        Player.objects.all().delete()
        return super().tearDown()

    @ classmethod
    def tearDownClass(cls) -> None:
        if User.objects.all().count() > 0:
            User.objects.all().delete()
        return super().tearDownClass()


class PlayerTest(TestCase):
    def create_unique_email(self):
        self.unique_email = f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        self.unique_username = f'user_{uuid.uuid4().hex[:10]}'

    def setUp(self):
        self.create_unique_email()
        self.create_unique_username()
        self.token = Token.objects.create()

        self.event = Event.objects.create(name='Evento 1', token=self.token)
        self.user = User.objects.create(
            username=self.unique_username, email='test@user1.com', first_name='Test', last_name='User')
        self.player = Player.objects.create(
            user=self.user, event=self.event, registration_email=self.unique_email)
        self.sumulaImortal = SumulaImortal.objects.create(
            name='Sumula 1', event=self.event)

    def test_create_player(self):
        self.assertIsNotNone(self.user)
        self.assertIsNotNone(self.player)
        self.assertEqual(self.player.registration_email, self.unique_email)
        self.assertEqual(self.player.user.username, self.unique_username)

    def test_update_total_score(self):
        self.assertEqual(self.player.total_score, 0)

        # Create player scores
        PlayerScore.objects.create(
            player=self.player, event=self.event, sumula_imortal=self.sumulaImortal, points=10)
        PlayerScore.objects.create(
            player=self.player, event=self.event, sumula_imortal=self.sumulaImortal, points=20)

        # Check if total score is updated
        self.assertEqual(self.player.total_score, 30)

    def test_update_total_score_alredy_with_score(self):
        self.assertEqual(self.player.total_score, 0)

        # Create player scores
        PlayerScore.objects.create(
            player=self.player, event=self.event, sumula_imortal=self.sumulaImortal, points=10)
        PlayerScore.objects.create(
            player=self.player, event=self.event, sumula_imortal=self.sumulaImortal, points=20)

        # Check if total score is updated
        self.assertEqual(self.player.total_score, 30)

        # Create another player score
        PlayerScore.objects.create(
            player=self.player, event=self.event, sumula_imortal=self.sumulaImortal, points=5)

        # Check if total score is updated
        self.assertEqual(self.player.total_score, 35)

    def tearDown(self):
        self.token.delete()
        self.user.delete()
        self.event.delete()
        self.player.delete()
        self.unique_email = None
        self.sumulaImortal.delete()

    @classmethod
    def tearDownClass(cls) -> None:
        if User.objects.all().count() > 0:
            User.objects.all().delete()
        return super().tearDownClass()


class StaffTest(TestCase):
    def create_unique_email(self):
        self.unique_email = f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        self.unique_username = f'user_{uuid.uuid4().hex[:10]}'

    def setUp(self):
        self.create_unique_email()
        self.create_unique_username()
        self.user = User.objects.create(
            username=self.unique_username, email=self.unique_email, first_name='Test', last_name='User')
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)
        self.staff = Staff.objects.create(
            full_name='Test User', registration_email=self.unique_email, user=self.user, event=self.event)

    def test_create_staff(self):
        self.assertIsNotNone(self.staff)
        self.assertEqual(self.staff.full_name, 'Test User')
        self.assertEqual(self.staff.registration_email, self.unique_email)

    def test_create_staff_without_email(self):
        with self.assertRaises(IntegrityError):
            Staff.objects.create(full_name='Test User')

    def test_edit_staff_name(self):
        self.staff.full_name = 'Test User 2'
        self.staff.save()
        self.assertEqual(self.staff.full_name, 'Test User 2')

    def test_edit_staff_email(self):
        self.staff.registration_email = 'another@email.com'
        self.staff.save()
        self.assertEqual(self.staff.registration_email, 'another@email.com')
