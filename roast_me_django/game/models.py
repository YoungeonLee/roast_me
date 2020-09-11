from django.db import models
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.dispatch import receiver
import os
from django.core.validators import validate_image_file_extension
from django.db.models import Q
import random


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
    # state {0: not-started, 1: voting, 2: picking, 3:result, 4: winner}
    state = models.IntegerField()
    round_length = models.IntegerField()
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name}: {self.num_of_players()}/{self.max_people}"

    def json_data(self):
        game = {"state": self.state}
        game["timer"] = self.round_length
        game["players"] = {}
        for player in self.player.order_by('pk'):
            game["players"][player.user.username] = {"score": player.score, "state":player.state, "admin":player.admin, "image": "../../../" + str(player.user.image)}
        game["roastee"] = {}
        roastee = self.roastee()
        if roastee:
            game["roastee"]["imgLink"] = "../../../" + str(roastee.user.image)
            game["roastee"]["username"] = roastee.user.username
            game["roastee"]["description"] = roastee.user.description
        else:
            game["roastee"]["imgLink"] = ""
            game["roastee"]["username"] = ""
            game["roastee"]["description"] = ""
        game["roast"] = {}
        if self.state == 2:
            for roast in self.roast.all():
                game["roast"][roast.player.user.username] = roast.roast
        game["selectedRoast"] = ""
        game["roundWinner"] = ""
        if self.roast.filter(selected=True).exists():
            selected_roast = self.roast.get(selected=True)
            game["selectedRoast"] = selected_roast.roast
            game["roundWinner"] = selected_roast.player.user.username
        game["winner"] = ""
        game["winner"]
        winner = self.winner()
        if winner:
            game["winner"] = winner.user.username
        game["time"] = self.time.isoformat()
        print(self.time)
        return game
        
    def roastee(self):
        if self.player.filter(state=1).exists():
            return self.player.get(state=1)
        return None

    def judge(self):
        if self.player.filter(state=2).exists():
            return self.player.get(state=2)
        return None

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

    def empty(self):
        return self.num_of_players() == 0

    def make_admin(self):
        print("make admin")
        if self.player.all().exists():
            new_admin = self.player.order_by().first()
            new_admin.admin = True
            new_admin.save()

    def startable(self):
        return self.num_of_players() >= 4

    def next_round(self, winner):
        print("next round")
        self.clear_roasts()
        self.clear_submissions()
        self.player.get(state=2).change_state(0)
        winner.change_state(2)
        next_roastee = random.choice(self.player.filter(state=0))
        self.player.get(state=1).change_state(0)
        next_roastee.change_state(1)
        self.change_state(1)



    def shuffle(self):
        print("shuffle")
        self.clear_roasts()
        self.clear_submissions()
        for player in self.player.filter(Q(state=1) | Q(state=2)):
            player.change_state(0)
        choices = self.player.filter(state=0)
        random.choice(choices).change_state(1)
        choices = self.player.filter(state=0)
        random.choice(choices).change_state(2)
        if self.state == 4:
            for player in self.player.all():
                player.reset_score()
        self.change_state(1)
    
    def skip(self):
        print("skip")
        if self.state == 1:
            if len(self.roast.all()) == 0:
                self.shuffle()
            else:
                self.clear_submissions()
                self.change_state(2)
        elif self.state == 2:
            self.shuffle()
            
        

    def reset_timer(self):
        self.time = timezone.now()
        self.save()

    def change_state(self, state):
        self.state = state
        self.reset_timer()

    def roast_complete(self):
        return len(self.player.filter(state=0)) == len(self.roast.all())

    def clear_submissions(self):
        players = self.player.filter(submitted=True)
        for player in players:
            player.clear_submission()
    
    def clear_roasts(self):
        self.roast.all().delete()

    def create_roastee(self):
        players = self.player.filter(state=0)
        random.choice(players).change_state(1)

    def create_judge(self):
        players = self.player.filter(state=0)
        random.choice(players).change_state(2)
        



    


class Player(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="player")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="player")
    score = models.IntegerField()
    # state {0: roaster, 1: roastee, 2: judge}
    state = models.IntegerField()
    submitted = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} in {self.game}"
        
    def add_score(self):
        self.score += 1
        self.save()
    
    def reset_score(self):
        self.score = 0
        self.save()

    def startable(self):
        return self.game.startable() and self.admin

    def player_info(self):
        return {
            "admin": self.admin,
            "button": self.startable(),
            "state": self.state,
            "submitted": self.submitted
        }

    def check_submission(self):
        self.submitted = True
        self.save()

    def clear_submission(self):
        self.submitted = False
        self.save()

    def change_state(self, state):
        self.state = state 
        self.save()


        
class Roast(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="roast")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="roast")
    roast = models.CharField(max_length=100)
    selected = models.BooleanField(default=False)

    def select(self):
        self.selected = True
        self.save()

