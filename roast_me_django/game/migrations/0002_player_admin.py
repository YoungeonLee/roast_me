# Generated by Django 3.1 on 2020-08-22 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='admin',
            field=models.BooleanField(default=False),
        ),
    ]
