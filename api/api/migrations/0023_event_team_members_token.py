# Generated by Django 5.0.3 on 2024-04-21 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_alter_playertotalscore_total_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='team_members_token',
            field=models.CharField(default='', max_length=8, unique=True),
        ),
    ]
