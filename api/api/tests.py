from django.test import TestCase
from api.models import Token, Event, Sumula, PlayerScore
from users.models import User
from unittest import TestCase

# Create your tests here.


class ModelsTestCase(TestCase):
    def setUp(self):
        """Cria usuarios para os testes"""
        self.user, _ = User.objects.get_or_create(
            first_name='Joao', last_name='Silva', email='JoaoSilva@hotmail.com', picture_url="https://photo.aqui.com", username='JoaoSilva@hotmail.com')
        self.user.save()
        self.user_2, _ = User.objects.get_or_create(
            first_name='Pedro', last_name='Silva', email='PedroSilva@gmail.com', picture_url="https://photo.aqui.com", username="PedroSilva@gmail.com")
        self.user_2.save()
        self.user_3, _ = User.objects.get_or_create(
            first_name='Maria', last_name='Silva', email="MariaSilva@gmail.com", picture_url="https://photo.aqui.com", username="MariaSilva@gmail.com")
        self.user_3.save()

    def test_create_token(self):
        """Testa a criacao de um token e sua validade"""
        token = Token.objects.create()
        token_code = token.generate_token()
        self.assertIsNotNone(token)
        self.assertEqual(len(token_code), 8)
        self.assertEqual(token.token_code, token_code)
    def test_unique_token_with_same_code(self):
        """Testa a criacao de tokens com o mesmo codigo"""
        token = Token.objects.create()
        token_code = token.generate_token()
        token_2 = Token.objects.create(token_code=token_code)
        self.assertNotEqual(token.token_code, token_2.token_code)