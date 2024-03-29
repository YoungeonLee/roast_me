# Generated by Django 3.1 on 2020-08-19 08:27

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('max_people', models.IntegerField()),
                ('goal_score', models.IntegerField()),
                ('state', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100, unique=True)),
                ('image', models.ImageField(upload_to='images', validators=[django.core.validators.validate_image_file_extension])),
                ('description', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user', to='sessions.session')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('state', models.IntegerField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player', to='game.game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player', to='game.profile')),
            ],
        ),
    ]
