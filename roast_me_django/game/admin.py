from django.contrib import admin

# Register your models here.
from .models import User, Games
admin.site.register(User)
admin.site.register(Games)
