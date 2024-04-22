from django.db import models
from users.models import User
import string
import random

TOKEN_LENGTH = 8


class Token (models.Model):
    """Modelo de Token. Um token é um codigo de uso unico utilizado para criar um evento"

    fields:
    - token_code: CharField com o código do token
    - used: BooleanField que indica se o token foi utilizado ou não
    """
    token_code = models.CharField(
        default='', max_length=TOKEN_LENGTH, unique=True)
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = ("Token")
        verbose_name_plural = ("Tokens")

    def __str__(self) -> str:
        return self.token_code

    def is_used(self) -> bool:
        """Retorna se o token foi utilizado ou não."""
        return self.used

    def mark_as_used(self) -> None:
        """Marca o token como utilizado."""
        self.used = True
        self.save()

    def generate_token(self) -> str:
        """Gera um token aleatório de TOKEN_LENGTH caracteres."""
        self.token_code = ''.join(random.choices(
            string.ascii_letters + string.digits, k=TOKEN_LENGTH))
        return self.token_code

    def save(self, *args, **kwargs) -> None:
        """Sobrescreve o método save para gerar um token caso não exista."""
        if not self.token_code:
            self.generate_token()
        super(Token, self).save(*args, **kwargs)


class Event (models.Model):
    """Modelo de Evento. Um evento esta associado a um token de uso unico e possui multiplas models Sumula associadas.
     fields:
    - token: ForeignKey para Token
    - name: CharField com o nome do evento
    """
    token = models.OneToOneField(
        Token, on_delete=models.CASCADE, related_name='event')
    name = models.CharField(default='', max_length=64)
    team_members_token = models.CharField(
        default='', max_length=TOKEN_LENGTH, unique=True)
    

    class Meta:
        verbose_name = ("Evento")
        verbose_name_plural = ("Eventos")

    def __str__(self):
        return self.name

    def __token__(self):
        return self.token.token_code

    def generate_team_members_token(self) -> str:
        """Gera um token aleatório de TOKEN_LENGTH caracteres."""
        self.team_members_token = ''.join(random.choices(
            string.ascii_letters + string.digits, k=TOKEN_LENGTH))
        return self.team_members_token

    def save(self, *args, **kwargs) -> None:
        """Sobrescreve o método save para gerar um token caso não exista."""
        if not self.team_members_token:
            self.generate_team_members_token()
        super(Event, self).save(*args, **kwargs)


class Sumula (models.Model):
    """Modelo de Sumula.
    - referee: ManyToManyField para User
    - event: ForeignKey para Event
    - name: CharField com o nome da sumula
    """
    referee = models.ManyToManyField(User, related_name='sumulas', blank=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='event_sumulas')
    name = models.CharField(default='', max_length=64)

    class Meta:
        verbose_name = ("Sumula")
        verbose_name_plural = ("Sumulas")

    def __str__(self):
        return self.name


class PlayerScore(models.Model):
    """ Modelo para salvar pontuacao dos players.
    fields:
    - user: ForeignKey para User
    - event: ForeignKey para Event
    - sumula: ForeignKey para Sumula
    - points: IntegerField com a pontuacao do player
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='player_score')
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='player_score')
    sumula = models.ForeignKey(
        Sumula, on_delete=models.CASCADE, related_name='player_score')
    points = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = ("PlayerScore")
        verbose_name_plural = ("PlayerScores")

    def __str__(self):
        return str(self.points)


class PlayerTotalScore(models.Model):
    """Armaneza a pontuacao total de um usuario em um evento.
    Apenas um PlayerTotalScore por usuario e evento é permitido.
    fields:
    - user: ForeignKey para User
    - event: ForeignKey para Event
    - total_points: IntegerField com a pontuacao total do usuario
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='total_score')
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='total_score')
    total_points = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = ("PlayerTotalScore")
        verbose_name_plural = ("PlayerTotalScores")
        unique_together = ['user', 'event']

    def __str__(self):
        return str(self.total_points)
