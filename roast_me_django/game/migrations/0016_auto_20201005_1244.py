# Generated by Django 3.1 on 2020-10-05 12:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0015_message_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]