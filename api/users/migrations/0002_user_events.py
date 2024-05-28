# Generated by Django 5.0.3 on 2024-05-28 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_token_created_at'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='events',
            field=models.ManyToManyField(blank=True, related_name='users', to='api.event'),
        ),
    ]