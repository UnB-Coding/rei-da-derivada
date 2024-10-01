from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """
    This model is used to store user information.
    params:
    - uuid: UUIDField
    - first_name: CharField
    - last_name: CharField
    - email: EmailField
    - picture_url: URLField
    - is_active: BooleanField
    - events: ManyToManyField
    """
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    first_name = models.CharField(default='', max_length=64, blank=True)
    last_name = models.CharField(default='', max_length=128, blank=True)
    email = models.EmailField(blank=False, unique=True)
    picture_url = models.URLField(default='')
    is_active = models.BooleanField(default=True)
    events = models.ManyToManyField(
        'api.Event', related_name="users", blank=True)
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
