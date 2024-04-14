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
    """
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    first_name = models.CharField(default='', max_length=64)
    last_name = models.CharField(default='', max_length=128)
    email = models.EmailField(blank=False, unique=True)
    picture_url = models.URLField(default='')
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = ["email"]

# Falta terminar de adicionar as permissioes e fazer as views.


class CustomUsersPermissions:
    class Meta:
        permissions = (
            ("can_create_event", 'Can create an event'),
            ("can_edit_event", 'Can edit an event'),
            ("can_delete_event", 'Can delete an event'),
            ("can_create_sumula", 'Can create a sumula'),
            ("can_edit_sumula", 'Can edit a sumula'),
            ("can_delete_sumula", 'Can delete a sumula')

        )
