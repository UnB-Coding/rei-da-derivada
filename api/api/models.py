import random
from django.db import IntegrityError, models
from django.forms import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete
from django.db.models import Sum, F
from users.models import User
import string
import secrets
TOKEN_LENGTH = 9


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
        alphabet = string.ascii_uppercase
        while True:
            letters = ''.join(secrets.choice(alphabet)
                              for i in range(TOKEN_LENGTH - 2))
            numbers = ''.join(secrets.choice(string.digits)
                              for i in range(2))
            self.token_code = ''.join(random.sample(
                letters + numbers, len(letters + numbers)))
            if not Token.objects.filter(token_code=self.token_code).exists():
                break

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
    join_token = models.CharField(
        default='', max_length=TOKEN_LENGTH, blank=True)
    name = models.CharField(default='', max_length=64, blank=True, null=True)
    active = models.BooleanField(default=True)
    admin_email = models.EmailField(default='', blank=True, null=True)
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
        alphabet = string.ascii_uppercase
        while True:
            letters = ''.join(secrets.choice(alphabet)
                              for i in range(TOKEN_LENGTH - 2))
            numbers = ''.join(secrets.choice(string.digits)
                              for i in range(2))
            self.join_token = ''.join(random.sample(
                letters + numbers, len(letters + numbers)))
            if not Event.objects.filter(join_token=self.join_token).exists():
                break

    def is_active(self) -> bool:
        """Retorna se o evento está ativo ou não."""
        return self.active

    def save(self, *args, **kwargs) -> None:
        """Sobrescreve o método save para gerar um token caso não exista."""
        if not self.join_token:
            self.generate_token()
        super(Event, self).save(*args, **kwargs)


class Staff(models.Model):
    """ Modelo para salvar informações de staff em um evento.
    fields:
    - full_name: CharField com o nome completo do staff
    - registration_email: EmailField
    - is_manager: BooleanField que indica se o staff é um manager
    - event: ForeignKey para Event
    - user: ForeignKey para User
    """
    full_name = models.CharField(
        default='', max_length=128, blank=True, null=True)
    registration_email = models.EmailField(
        default='',  blank=False, unique=False, null=False)
    is_manager = models.BooleanField(default=False)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='staff')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='staff', null=True, blank=True, default=None)

    class Meta:
        verbose_name = ("Staff")
        verbose_name_plural = ("Staffs")
        unique_together = ['user', 'event']

    def __str__(self) -> str:
        return f'{self.full_name}'


class Sumula (models.Model):
    """Modelo Base de Sumula.
    - referee: ManyToManyField para Staff (related_name='sumulas')
    - event: ForeignKey para Event
    - name: CharField com o nome da sumula
    """
    referee = models.ManyToManyField(Staff, blank=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE)
    name = models.CharField(default='', max_length=64)
    active = models.BooleanField(default=True)
    description = models.TextField(
        default='', blank=True, null=True, max_length=256)

    class Meta:
        abstract = True
        verbose_name = ("Sumula")
        verbose_name_plural = ("Sumulas")

    def __str__(self):
        return self.name


class SumulaImortal(Sumula):
    """Modelo de Sumula Imortal.
    - referee: ManyToManyField para Staff (related_name='sumulas')
    - event: ForeignKey para Event
    - name: CharField com o nome da sumula
    """
    referee = models.ManyToManyField(
        Staff, related_name='sumula_imortal', blank=True)

    class Meta:
        verbose_name = ("Sumula Imortal")
        verbose_name_plural = ("Sumulas Imortais")


class SumulaClassificatoria(Sumula):
    """Modelo de Sumula Classificatoria.
    - referee: ManyToManyField para Staff (related_name='sumulas')
    - event: ForeignKey para Event
    - name: CharField com o nome da sumula
    """
    referee = models.ManyToManyField(
        Staff, related_name='sumula_classificatoria', blank=True)

    class Meta:
        verbose_name = ("Sumula Classificatoria")
        verbose_name_plural = ("Sumulas Classificatoria")


class Player(models.Model):
    """
    This model is used to store player information.
    params:
    - full_name: CharField with the full name of the player
    - social_name: CharField with the social name of the player
    - user: ForeignKey to User
    - event: ForeignKey to Event
    - registration_email: EmailField
    - total_score: IntegerField
    """
    full_name = models.CharField(
        default='', max_length=128, blank=True, null=True)
    social_name = models.CharField(
        default='', max_length=128, blank=True, null=True)
    total_score = models.PositiveSmallIntegerField(default=0)
    registration_email = models.EmailField(
        blank=True, unique=False, null=True)
    is_imortal = models.BooleanField(default=False)
    is_present = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='player', null=True, blank=True, default=None)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='player')

    class Meta:
        verbose_name = ("Player")
        verbose_name_plural = ("Players")
        unique_together = ['user', 'event']

    # Atualiza a pontuação total após salvar uma instância de PlayerScore
    @receiver(post_save, sender='api.PlayerScore')
    def update_player_total_score_on_save(sender, instance, **kwargs):
        if instance.player and instance.player.event == instance.event:
            instance.player.total_score = PlayerScore.objects.filter(
                player=instance.player, event=instance.event).aggregate(Sum('points'))['points__sum'] or 0
            instance.player.save()

    # Atualiza a pontuação total após deletar uma instância de PlayerScore
    @receiver(pre_delete, sender='api.PlayerScore')
    def update_player_total_score_on_delete(sender, instance, **kwargs):
        if instance.player and instance.player.event == instance.event:
            instance.player.total_score -= instance.points
            if instance.player.total_score < 0:
                instance.player.total_score = 0
            instance.player.save()

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
        Player, on_delete=models.CASCADE, related_name='scores', default=None, blank=False, null=False)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='scores', default=None, blank=False, null=False)
    sumula_classificatoria = models.ForeignKey(
        SumulaClassificatoria, on_delete=models.CASCADE, related_name='scores', null=True, blank=True, default=None)
    sumula_imortal = models.ForeignKey(
        SumulaImortal, on_delete=models.CASCADE, related_name='scores', null=True, blank=True, default=None)
    points = models.PositiveSmallIntegerField(
        default=0, blank=False, null=False)

    class Meta:
        verbose_name = ("PlayerScore")
        verbose_name_plural = ("PlayerScores")

    def __str__(self):
        return f'{self.player} - {self.points}'

    def save(self, *args, **kwargs):
        if self.player is None or self.event is None:
            raise IntegrityError("Player e Evento são campos obrigatórios!")
        try:
            self.validar_evento_player()
            self.validar_evento_sumula()
            self.validar_sumulas()
        except ValidationError as e:
            raise ValidationError(e)
        super().save(*args, **kwargs)

    def validar_sumulas(self):
        if not any([self.sumula_classificatoria, self.sumula_imortal]):
            raise ValidationError(
                "Pelo menos um dos campos sumula_classificatoria ou sumula_imortal deve ser preenchido.")
        if all([self.sumula_classificatoria, self.sumula_imortal]):
            raise ValidationError(
                "Apenas um dos campos sumula_classificatoria ou sumula_imortal deve ser preenchido.")

    def validar_evento_player(self):
        if self.player.event != self.event:
            raise ValidationError(
                "O evento de Player deve ser o mesmo Evento do objeto de PlayerScore!")

    def validar_evento_sumula(self):
        if self.sumula_classificatoria and self.sumula_classificatoria.event != self.event:
            raise ValidationError(
                "O evento de uma Sumula deve ser o mesmo Evento do objeto de PlayerScore!")
        elif self.sumula_imortal and self.sumula_imortal.event != self.event:
            raise ValidationError(
                "O evento de uma Sumula deve ser o mesmo Evento do objeto de PlayerScore!")
        # if self.player is not None and self.event is not None:
        #     self.player.update_total_score(self.event)

    # def delete(self, *args, **kwargs):
    #     player = self.player
    #     event = self.event
    #     if player and event:
    #         super(PlayerScore, self).delete(*args, **kwargs)
    #         player.update_total_score(event)
    #     else:
    #         super(PlayerScore, self).delete(*args, **kwargs)
