# Generated by Django 5.0.3 on 2024-06-12 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_merge_20240612_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sumula',
            name='referee',
            field=models.ManyToManyField(blank=True, related_name='sumulas', to='api.staff'),
        ),
    ]
