# Generated by Django 3.1 on 2020-10-05 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0013_auto_20201001_1621'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=400)),
            ],
        ),
    ]