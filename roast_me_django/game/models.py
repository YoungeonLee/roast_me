from django.db import models

# Create your models here.
class User(models.Model):
    user_name = models.CharField(max_length=16)
    age = models.IntegerField()

    def __str__(self):
        return f"{self.user_name}: {self.age}"

class Games(models.Model):
    name = models.CharField(max_length=10)
    num_people = models.IntegerField()
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='host', null=True)
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamer', null=True)

    def __str__(self):
        return f"{self.name} hosted by {self.admin}: {self.player}({self.num_people})"
