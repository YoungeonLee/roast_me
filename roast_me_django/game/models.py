from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name= "user")
    image = models.ImageField(upload_to="images")
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"Profile of {self.user}"
"""
class User(models.Model):
    user_name = models.CharField(max_length=16)
    age = models.IntegerField()

    def __str__(self):
        return f"{self.user_name}: {self.age}"

class Game(models.Model):
    name = models.CharField(max_length=10)
    num_people = models.IntegerField()
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='host', null=True)
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamer', null=True)
    creation_time = models.DateTimeField()
    def __str__(self):
        return f"{self.name} hosted by {self.admin}: {self.player}({self.num_people})"
"""