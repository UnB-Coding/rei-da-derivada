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
        self.token_code = ''.join(
            random.choices(string.digits, k=TOKEN_LENGTH))
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
    name = models.CharField(default='', max_length=64, blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = ("Evento")
        verbose_name_plural = ("Eventos")

    def __str__(self):
        return self.name

    def __token__(self):
        return self.token.token_code


class Sumula (models.Model):
    """Modelo de Sumula.
    - referee: ManyToManyField para User (related_name='sumulas')
    - event: ForeignKey para Event
    - name: CharField com o nome da sumula
    """
    referee = models.ManyToManyField(User, related_name='sumulas', blank=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='sumulas')
    name = models.CharField(default='', max_length=64)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = ("Sumula")
        verbose_name_plural = ("Sumulas")

    def __str__(self):
        return self.name


class Player(models.Model):
    """
    This model is used to store player information.
    params:
    - user: OneToOneField to User
    - event: ForeignKey to Event
    - registration_email: EmailField
    - total_score: IntegerField
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='player')
    total_score = models.PositiveSmallIntegerField(default=0)
    registration_email = models.EmailField(blank=False, unique=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='players')

    class Meta:
        verbose_name = ("Player")
        verbose_name_plural = ("Players")
        unique_together = ['registration_email', 'event']

    def update_total_score(self, event):
        """ Calculate the total score of the player for an event. """
        self.total_score = PlayerScore.objects.filter(
            player=self, event=event
        ).aggregate(total=models.Sum('points'))['total'] or 0
        self.save()

    def __str__(self) -> str:
        return self.user.__str__()


class PlayerScore(models.Model):
    """ Modelo para salvar pontuacao dos players.
    fields:
    - player: ForeignKey para Player
    - event: ForeignKey para Event
    - sumula: ForeignKey para Sumula
    - points: IntegerField com a pontuacao do player
    """
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='scores')
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='scores')
    sumula = models.ForeignKey(
        Sumula, on_delete=models.CASCADE, related_name='scores')
    points = models.PositiveSmallIntegerField(
        default=0, blank=False, null=False)

    class Meta:
        verbose_name = ("PlayerScore")
        verbose_name_plural = ("PlayerScores")

    def __str__(self):
        return str(self.points)

    def save(self, *args, **kwargs) -> None:
        super(PlayerScore, self).save(*args, **kwargs)

        if self.player is not None and self.event is not None:
            self.player.update_total_score(self.event)
