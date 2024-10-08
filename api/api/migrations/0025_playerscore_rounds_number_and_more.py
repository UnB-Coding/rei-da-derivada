# Generated by Django 5.0.3 on 2024-07-31 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_player_is_present'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerscore',
            name='rounds_number',
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='sumulaclassificatoria',
            name='rounds',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='sumulaimortal',
            name='rounds',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
