# Generated by Django 5.0.3 on 2024-05-29 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='registration_email',
            field=models.EmailField(default='', max_length=254),
        ),
    ]
