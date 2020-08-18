from django.urls import path
from . import views

app_name = 'game'
urlpatterns = [
    path("", views.index, name="index"),
    path('games/', views.games, name='games'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('images/<str:filename>', views.render_image, name='image'),
]