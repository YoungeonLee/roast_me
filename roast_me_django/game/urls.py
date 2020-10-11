from django.urls import path
from . import views

app_name = 'game'
urlpatterns = [
    path("", views.index, name="index"),
    path('games/', views.games, name='games'),
    path('images/<str:filename>', views.render_image, name='image'),
    path('setprofile/', views.setprofile, name="setprofile"),
    path('profile/', views.profile, name='profile'),
    path('games/room/<str:room_name>/', views.room, name='room'),
    path('games/creategame/', views.creategame, name='creategame'),
    path('support/', views.support, name="support"),
    path('static/<str:app>/<str:filename>', views.static, name="static")
]