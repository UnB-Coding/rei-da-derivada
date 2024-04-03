from django.db import models
from users.models import User
from django.urls import reverse

# Modelo de Token. Um token é um codigo de uso unico utilizado para criar um evento
class Token (models.Model):
    code = models.CharField(default='', max_length=10, unique=True)

    class Meta:
        verbose_name = ("Token")
        verbose_name_plural = ("Tokens")

    def __str__(self):
        return self.code

# Modelo de Evento. Um evento esta associado a um token de uso unico e possui multiplas sumulas associadas.


class Event (models.Model):
    token = models.OneToOneField(
        Token, on_delete=models.CASCADE, related_name='token')

    class Meta:
        verbose_name = ("Evento")
        verbose_name_plural = ("Eventos")

    def __str__(self):
        return self.name

# Modelo de sumula. Uma sumula possui um nome


class Sumula (models.Model):
    name = models.CharField(default='', max_length=64)
    players = models.ManyToManyField(User, related_name='players')
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='event')

    class Meta:
        verbose_name = ("Sumula ")
        verbose_name_plural = ("Sumulas")

    def __str__(self):
        return self.name
