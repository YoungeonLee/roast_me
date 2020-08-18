from django.contrib import admin

# Register your models here.
from .models import Profile

admin.site.site_header = "Roast Me Admin"
admin.site.site_title = "Roast Me Admin"
admin.site.index_title = "Roast Me Administration"
admin.site.register(Profile)
