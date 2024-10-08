# Generated by Django 5.0.3 on 2024-08-11 19:21

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_alter_results_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='player',
            unique_together={('user', 'event', 'registration_email')},
        ),
    ]
