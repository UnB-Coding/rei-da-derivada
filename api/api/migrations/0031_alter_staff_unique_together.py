# Generated by Django 5.0.3 on 2024-08-11 19:27

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_alter_player_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='staff',
            unique_together={('user', 'event', 'registration_email')},
        ),
    ]