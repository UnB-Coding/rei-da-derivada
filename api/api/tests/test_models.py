from math import e
from django.db import IntegrityError
from django.test import TestCase
from api.models import Token, Event, Sumula, PlayerScore, TOKEN_LENGTH
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
        print(self.token.token_code)
        self.token.token_code = "ABC123"
        print(self.token.token_code)

    def test_token_str(self):
        """Testa a representação de um token"""
        self.assertEqual(self.token.__str__(),
                         ("Token: " + self.token.token_code))


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

    def test_edit_event_name(self):
        """Testa a edição do nome de um evento"""
        event = Event.objects.create(name='Evento 1', token=self.token)
        event.name = 'Evento 2'
        event.save()
        self.assertEqual(event.name, 'Evento 2')

    def test_delete_token_with_event(self):
        """Testa a deleção de um token com eventos associados"""
        event = Event.objects.create(name='Evento 1', token=self.token)
        self.token.delete()
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(name='Evento 1')

    def test_event_str(self):
        """Testa a representação de um evento"""
        event = Event.objects.create(name='Evento 1', token=self.token)
        self.assertEqual(event.__str__(),
                         "Evento: Evento 1 - Token: " + event.token.token_code)
