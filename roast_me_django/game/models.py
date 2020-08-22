from django.db import models
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.dispatch import receiver
import os
from django.core.validators import validate_image_file_extension

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(Session, on_delete=models.CASCADE, related_name= "user")
    username = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="images", validators=[validate_image_file_extension])
    description = models.CharField(max_length=100)


    def __str__(self):
        return f"Profile of {self.username}"

@receiver(models.signals.post_delete, sender=Profile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Profile` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(models.signals.pre_save, sender=Profile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `Profile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Profile.objects.get(pk=instance.pk).image
    except Profile.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
"""
class User(models.Model):
    user_name = models.CharField(max_length=16)
    age = models.IntegerField()

    def __str__(self):
        return f"{self.user_name}: {self.age}"
"""
class Game(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    max_people = models.IntegerField()
    goal_score = models.IntegerField()
    # state {0: not-started, 1: started}
    state = models.IntegerField()

    def __str__(self):
        return f"{self.name}: {self.num_of_players()}/{self.max_people}"

    def json_data(self):
        players = {}
        for player in self.player.all():
            players[player.user.username] = {"score": player.score, "state":player.state}
        return {
            "players": players,
        }
    def roastee(self):
        return self.player.get(state=1)

    def judge(self):
        return self.player.get(state=2)

    def num_of_players(self):
        return len(self.player.all())

    def winner(self):
        won = self.player.filter(score__gte=self.goal_score)
        if len(won) >= 1:
            return won[0]
        else:
            return False

    def full(self):
        return self.num_of_players() >= self.max_people


    


class Player(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="player")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="player")
    score = models.IntegerField()
    # state {0: roaster, 1: roastee, 2: judge}
    state = models.IntegerField()

    def __str__(self):
        return f"{self.user} in {self.game}"
        
    def add_score(self):
        self.score += 1
        self.save()
        

