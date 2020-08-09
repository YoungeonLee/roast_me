from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('games/', views.games, name='games'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout')
]