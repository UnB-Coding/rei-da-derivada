from django.db import IntegrityError
from django.test import TestCase
from api.models import PlayerTotalScore, Token, Event, Sumula, PlayerScore, TOKEN_LENGTH
from users.models import User
from unittest import TestCase

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


class EventTest(TestCase):
    def setUp(self):
        self.token = Token.objects.create()
        self.token.save()

    def test_create_event(self):
        """Testa a criação de um evento"""
        event = Event.objects.create(name='Evento 1', token=self.token)
        self.assertIsNotNone(event)
        self.assertEqual(event.name, 'Evento 1')

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

    def test_team_members_token_creation(self):
        """Testa a criação de um token de membros de equipe"""
        event = Event.objects.create(name='Evento 1', token=self.token)
        self.assertIsNotNone(event.team_members_token)
        self.assertTrue(len(event.team_members_token) == TOKEN_LENGTH)

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


class SumulaTest(TestCase):
    def setUp(self):
        self.token = Token.objects.create()
        self.user = User.objects.create(
            email='user1@gmail.com', username='user1')
        self.user_2 = User.objects.create(
            email='user2@gmail.com', username='user2')
        self.event = Event.objects.create(name='Evento 1', token=self.token)
        self.sumula = Sumula.objects.create(name='Sumula 1', event=self.event)

    def test_create_sumula_without_referee(self):
        """Testa a criação de uma sumula"""
        sumula = Sumula.objects.create(name='Sumula 2', event=self.event)
        self.assertEqual(sumula.name, 'Sumula 2')
        self.assertEqual(sumula.event, self.event)

    def test_add_referee_to_sumula(self):
        """Testa a criação de uma sumula com árbitros"""
        sumula = Sumula.objects.create(
            name='Sumula 1', event=self.event)
        sumula.referee.add(self.user)
        sumula.referee.add(self.user_2)
        self.assertIn(self.user, sumula.referee.all())
        self.assertIn(self.user_2, sumula.referee.all())

    def test_remove_one_referee_from_sumula(self):
        """Testa a remoção de um árbitro de uma sumula"""
        self.sumula.referee.add(self.user)
        self.sumula.referee.remove(self.user)
        self.assertNotIn(self.user, self.sumula.referee.all())

    def test_remove_all_referees_from_sumula(self):
        """Testa a remoção de todos os árbitros de uma sumula"""
        self.sumula.referee.add(self.user)
        self.sumula.referee.add(self.user_2)
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


class PlayerScoreTest(TestCase):
    def setUp(self):
        self.token = Token.objects.create()
        self.user = User.objects.create(
            email='user1@gmail.com', username='user1')
        self.event = Event.objects.create(name='Evento 1', token=self.token)
        self.sumula = Sumula.objects.create(name='Sumula 1', event=self.event)
        self.player_score = PlayerScore.objects.create(
            user=self.user, event=self.event, sumula=self.sumula, points=0)
        self.player_score.save()

    def test_create_empty_player_score(self):
        """Testa a criação de uma pontuação de jogador"""
        self.assertEqual(self.player_score.user, self.user)
        self.assertEqual(self.player_score.event, self.event)
        self.assertEqual(self.player_score.sumula, self.sumula)
        self.assertEqual(self.player_score.points, 0)

    def test_edit_points_to_player_score(self):
        self.player_score.points = 10
        self.player_score.save()
        self.assertEqual(self.player_score.points, 10)
        self.assertEqual(str(self.player_score), '10')

    def test_create_player_score_without_user(self):
        """Testa a criação de uma pontuação de jogador sem usuário"""
        with self.assertRaises(IntegrityError):
            PlayerScore.objects.create(event=self.event, sumula=self.sumula)

    def test_create_player_score_without_event(self):
        """Testa a criação de uma pontuação de jogador sem evento"""
        with self.assertRaises(IntegrityError):
            PlayerScore.objects.create(user=self.user, sumula=self.sumula)

    def test_create_player_score_without_sumula(self):
        """Testa a criação de uma pontuação de jogador sem sumula"""
        with self.assertRaises(IntegrityError):
            PlayerScore.objects.create(user=self.user, event=self.event)

    def test_create_player_score_without_points(self):
        """Testa a criação de uma pontuação de jogador sem pontos"""
        player_score = PlayerScore.objects.create(
            user=self.user, event=self.event, sumula=self.sumula)
        self.assertEqual(player_score.points, 0)

    def test_create_player_score_with_negative_points(self):
        """Testa a criação de uma pontuação de jogador com pontos negativos"""
        with self.assertRaises(IntegrityError):
            PlayerScore.objects.create(
                user=self.user, event=self.event, sumula=self.sumula, points=-10)

    def test_delete_player_score(self):
        """Testa a deleção de uma pontuação de jogador"""
        self.player_score.delete()
        with self.assertRaises(PlayerScore.DoesNotExist):
            PlayerScore.objects.get(
                user=self.user, event=self.event, sumula=self.sumula)

    def test_player_score_str(self):
        """Testa a representação de uma pontuação de jogador"""
        self.assertEqual(str(self.player_score), '0')

    def tearDown(self):
        self.token.delete()
        self.user.delete()
        self.event.delete()
        self.sumula.delete()
        if self.player_score.id is not None:
            self.player_score.delete()
        return super().tearDown()


class PlayerTotalScoreTest(TestCase):
    def setUp(self):
        self.token = Token.objects.create()
        self.user = User.objects.create(
            email='user1@gmail.com', username='user1', first_name='John', last_name='Doe')
        self.user_2 = User.objects.create(username='user2')
        self.event = Event.objects.create(name='Evento 1', token=self.token)
        self.player_total_score = PlayerTotalScore.objects.create(
            user=self.user, event=self.event, total_points=0)

    def test_create_player_total_score(self):
        """Testa a criação de uma pontuação total de jogador"""
        self.assertEqual(self.player_total_score.user, self.user)
        self.assertEqual(self.player_total_score.event, self.event)
        self.assertEqual(self.player_total_score.total_points, 0)

    def test_create_player_total_score_without_user(self):
        """Testa a criação de uma pontuação total de jogador sem usuário"""
        with self.assertRaises(IntegrityError):
            PlayerTotalScore.objects.create(event=self.event, total_points=0)

    def test_create_player_total_score_without_event(self):
        """Testa a criação de uma pontuação total de jogador sem evento"""
        with self.assertRaises(IntegrityError):
            PlayerTotalScore.objects.create(user=self.user, total_points=0)

    def test_create_player_total_score_without_points(self):
        """Testa a criação de uma pontuação total de jogador sem pontos"""
        player_total_score = PlayerTotalScore.objects.create(
            user=self.user_2, event=self.event)
        self.assertEqual(player_total_score.total_points, 0)

    def test_create_player_total_score_with_negative_points(self):
        """Testa a criação de uma pontuação total de jogador com pontos negativos"""
        with self.assertRaises(IntegrityError):
            PlayerTotalScore.objects.create(
                user=self.user, event=self.event, total_points=-10)

    def test_try_to_create_duplicate_player_total_score(self):
        """Testa a criação de uma pontuação total de jogador duplicada"""
        with self.assertRaises(IntegrityError):
            PlayerTotalScore.objects.create(
                user=self.user, event=self.event, total_points=0)

    def test_edit_total_points(self):
        """Testa a edição da pontuação total de jogador"""
        self.player_total_score.total_points = 10
        self.player_total_score.save()
        self.assertEqual(self.player_total_score.total_points, 10)

    def test_delete_player_total_score(self):
        """Testa a deleção de uma pontuação total de jogador"""
        self.player_total_score.delete()
        with self.assertRaises(PlayerTotalScore.DoesNotExist):
            PlayerTotalScore.objects.get(user=self.user, event=self.event)

    def test_player_total_score_str(self):
        """Testa a representação de uma pontuação total de jogador"""
        self.assertEqual(str(self.player_total_score), '0')

    def tearDown(self):
        self.user.delete()
        self.user_2.delete()
        self.token.delete()
        self.event.delete()
        if self.player_total_score.id is not None:
            self.player_total_score.delete()
        return super().tearDown()
