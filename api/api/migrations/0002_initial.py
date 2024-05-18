# Generated by Django 5.0.3 on 2024-05-18 20:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('api', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='playerscore',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='api.event'),
        ),
        migrations.AddField(
            model_name='playerscore',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='api.player'),
        ),
        migrations.AddField(
            model_name='sumula',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sumulas', to='api.event'),
        ),
        migrations.AddField(
            model_name='sumula',
            name='referee',
            field=models.ManyToManyField(blank=True, related_name='sumulas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='playerscore',
            name='sumula',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='api.sumula'),
        ),
        migrations.AddField(
            model_name='event',
            name='token',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='event', to='api.token'),
        ),
        migrations.AlterUniqueTogether(
            name='player',
            unique_together={('registration_email', 'event')},
        ),
    ]
