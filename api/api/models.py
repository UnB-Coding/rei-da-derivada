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
        default='', max_length=TOKEN_LENGTH, unique=True, blank=True)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, blank=True,)

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
    - active: BooleanField que indica se o evento está ativo ou não
    """
    token = models.OneToOneField(
        Token, on_delete=models.CASCADE, related_name='event')
    name = models.CharField(default='', max_length=64, blank=True, null=True)
    active = models.BooleanField(default=True)
    players_token = models.CharField(
        default='', max_length=TOKEN_LENGTH, blank=True, null=False, unique=True)
    results_published = models.BooleanField(default=False)

    class Meta:
        verbose_name = ("Evento")
        verbose_name_plural = ("Eventos")
        permissions = [
            ("add_sumula_event", "Can add sumula"),
            ("change_sumula_event", "Can change sumula"),
            ("view_sumula_event", "Can view sumula"),
            ("delete_sumula_event", "Can delete sumula"),
            ("add_player_event", "Can add player"),
            ("change_player_event", "Can change player"),
            ("view_player_event", "Can view player"),
            ("delete_player_event", "Can delete player"),
            ("add_player_score_event", "Can add player_score"),
            ("change_player_score_event", "Can change player_score"),
            ("view_player_score_event", "Can view player_score"),
            ("delete_player_score_event", "Can delete player_score"),
        ]

    def __str__(self):
        return self.name

    def __token__(self):
        return self.token.token_code

    def is_results_published(self) -> bool:
        return self.results_published

    def generate_token(self) -> str:
        """Gera um token aleatório de TOKEN_LENGTH caracteres."""
        self.players_token = ''.join(
            random.choices(string.digits, k=TOKEN_LENGTH))
        return self.players_token

    def save(self, *args, **kwargs) -> None:
        """Sobrescreve o método save para gerar um token caso não exista."""
        if not self.players_token:
            self.generate_token()
        if not self.token.is_used():
            self.token.mark_as_used()
        super(Event, self).save(*args, **kwargs)


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
    - full_name: CharField with the full name of the player
    - social_name: CharField with the social name of the player
    - user: OneToOneField to User
    - event: ForeignKey to Event
    - registration_email: EmailField
    - total_score: IntegerField
    """
    full_name = models.CharField(
        default='', max_length=128, blank=True, null=True)
    social_name = models.CharField(
        default='', max_length=128, blank=True, null=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='player', null=True, blank=True)
    total_score = models.PositiveSmallIntegerField(default=0)
    registration_email = models.EmailField(
        blank=False, unique=False, null=False)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='player')

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
        return self.full_name


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
