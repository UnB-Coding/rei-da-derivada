from django.db import models
from users.models import User
import string
import random

TOKEN_LENGTH = 8


class Token (models.Model):
    """Modelo de Token. Um token é um codigo de uso unico utilizado para criar um evento"""
    token_code = models.CharField(
        default='', max_length=TOKEN_LENGTH, unique=True)

    class Meta:
        verbose_name = ("Token")
        verbose_name_plural = ("Tokens")

    def __str__(self):
        return self.token_code

    def generate_token(self):
        self.token_code = ''.join(random.choices(
            string.ascii_letters + string.digits, k=TOKEN_LENGTH))
        # print(self.token_code)
        return self.token_code


class Event (models.Model):
    """Modelo de Evento. Um evento esta associado a um token de uso unico e possui multiplas models Sumula associadas."""
    token = models.OneToOneField(
        Token, on_delete=models.CASCADE, related_name='token')
    name = models.CharField(default='', max_length=64)

    class Meta:
        verbose_name = ("Evento")
        verbose_name_plural = ("Eventos")

    def __str__(self):
        return self.token.token_code


class Sumula (models.Model):
    """Modelo de sumula. Uma sumula esta associada a um unico evento.
    Possui arbitro e nome"""
    referee = models.ManyToManyField(User, related_name='referee')
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='event')
    name = models.CharField(default='', max_length=64)

    class Meta:
        verbose_name = ("Sumula")
        verbose_name_plural = ("Sumulas")

    def __str__(self):
        return self.name


class PlayerScore(models.Model):
    """ Modelo para salvar pontuacao dos players. 
    Cada instancia de PlayerScore esta associada com apenas um usuario, evento e sumula. """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='player_score')
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='player_score')
    sumula = models.ForeignKey(
        Sumula, on_delete=models.CASCADE, related_name='player_score')
    points = models.IntegerField(default=0)

    class Meta:
        verbose_name = ("PlayerScore")
        verbose_name_plural = ("PlayerScores")

    def __str__(self):
        return str(self.points)

# @receiver(post_save, sender=PlayerScore)


class PlayerTotalScore(models.Model):
    """Armaneza a pontuacao total de um usuario em um evento."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='total_scores')
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='total_scores')
    total_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}: {self.total_points} pontos"
