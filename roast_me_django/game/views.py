from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from .models import Profile
from pathlib import Path
from os.path import join
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
game_list = []

class SearchGameForm(forms.Form):
    game = forms.CharField(label='')
    


# Create your views here.
def index(request):
    return render(request, "game/index.html", {
        "user": request.user.is_authenticated
    })

def games(request):
    if request.method == "POST":
        form = SearchGameForm(request.POST)
        if form.is_valid():
            game = form.cleaned_data["game"]
            game_list.append(game)
            return HttpResponseRedirect(reverse('game:games'))
        else:
            return render(request, "game/games.html", {
                "user": request.user.is_authenticated,
                "games": game_list,
                "form": form
            })

    return render(request, "game/games.html", {
        "user": request.user.is_authenticated,
        "games": game_list,
        "form":SearchGameForm()
    })

def login_view(request):
    if request.method == "POST":
        #print(request.POST)
        ID = request.POST["InputID"]
        password = request.POST['InputPassword']
        user = authenticate(request, username=ID, password=password)
        if user is not None:
            login(request=request, user=user)
            return HttpResponseRedirect(reverse("game:index"))
        else:
            return render(request, "game/login.html",{
                "user": request.user.is_authenticated,
                "message": "Wrong ID or Password"
            })

    return render(request, 'game/login.html',{
        "user": request.user.is_authenticated
    })
    
def logout_view(request):
    logout(request)
    return render(request, "game/index.html",{
        "user": request.user.is_authenticated
    })

def signup_view(request):
    if request.method == "POST":
        print(request.POST)
        print(request.FILES)
        #print(request.POST)
        ID = request.POST["InputID"]
        password = request.POST['InputPassword']
        image = request.FILES['profileImage']
        image.name = f"{ID}.jpg"
        description = request.POST["description"]
        try:
            user = User.objects.create_user(ID, password=password)
        except IntegrityError:
            return render(request, "game/signup.html",{
                "user": request.user.is_authenticated,
                "message": "Given ID already exists"
            })
        profile = Profile(user=user, image=image, description=description)
        profile.save()
        user = authenticate(request, username=ID, password=password)
        login(request=request, user=user)
        return HttpResponseRedirect(reverse("game:index"))

    #get request
    return render(request, 'game/signup.html',{
        "user": request.user.is_authenticated
    })

def render_image(request, filename):
    with open(join(BASE_DIR, "images", filename), "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")