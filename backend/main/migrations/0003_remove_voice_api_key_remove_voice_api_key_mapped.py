# Generated by Django 5.0.6 on 2024-05-27 17:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_voice_api_key_voice_api_key_mapped'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voice',
            name='api_key',
        ),
        migrations.RemoveField(
            model_name='voice',
            name='api_key_mapped',
        ),
    ]
