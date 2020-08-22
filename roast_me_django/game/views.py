from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django import forms
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from .models import Profile, Game, Player
from pathlib import Path
from os.path import join
from PIL import Image, UnidentifiedImageError
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
game_list = []

class SearchGameForm(forms.Form):
    game = forms.CharField(label='')
    
def profile_exists(session):
    return Profile.objects.filter(user_id=session.session_key).exists()

# Create your views here.
def index(request):
    return render(request, "game/index.html", {
        "user": profile_exists(request.session)
    })

def games(request):
    print(request.session.keys())
    print(request.session.session_key)
    # if need to make profile
    if not profile_exists(request.session):
        return HttpResponseRedirect(reverse("game:setprofile"))
    
    if request.method == "POST":
        form = SearchGameForm(request.POST)
        if form.is_valid():
            game = form.cleaned_data["game"]
            game_list.append(game)
            return HttpResponseRedirect(reverse('game:games'))
        else:
            return render(request, "game/games.html", {
                "user": profile_exists(request.session),
                "games": game_list,
                "form": form
            })

    return render(request, "game/games.html", {
        "user": profile_exists(request.session),
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
                "user": profile_exists(request.session),
                "message": "Wrong ID or Password"
            })

    return render(request, 'game/login.html',{
        "user": profile_exists(request.session)
    })
    
def logout_view(request):
    logout(request)
    return render(request, "game/index.html",{
        "user": profile_exists(request.session)
    })

def signup_view(request):
    if request.method == "POST":
        print(request.POST)
        print(request.FILES)
        #print(request.POST)
        ID = request.POST["InputID"]
        password = request.POST['InputPassword']
        image = request.FILES['profileImage']
        description = request.POST["description"]
        try:
            user = User.objects.create_user(ID, password=password)
        except IntegrityError:
            return render(request, "game/signup.html",{
                "user": profile_exists(request.session),
                "message": "Given ID already exists"
            })
        profile = Profile(user=user, image=image, description=description)
        profile.save()
        user = authenticate(request, username=ID, password=password)
        login(request=request, user=user)
        return HttpResponseRedirect(reverse("game:index"))

    #get request
    return render(request, 'game/signup.html',{
        "user": profile_exists(request.session)
    })

def setprofile(request):
    # post request
    if request.method == "POST":
        print(request.POST)
        print(request.FILES)
        #print(request.POST)
        try:
            # check if all forms are valid
            ID = request.POST["InputID"]
            image = request.FILES['profileImage']
            print(type(image))
            description = request.POST["description"]
        except:
            return render(request, 'game/setprofile.html',{
                    "user": profile_exists(request.session),
                    "message": "Server Error; make sure you filled the entire form correctly"
                })
        
        try:
            # check if image is valid
            im=Image.open(image)
        except UnidentifiedImageError:
            return render(request, 'game/setprofile.html',{
                    "user": profile_exists(request.session),
                    "message": "Invalid image"
                })
            
        if profile_exists(request.session):
            profile = Profile.objects.get(user_id=request.session.session_key)
            profile.username = ID
            profile.image = image
            profile.description = description
            try:
                profile.save()
            except IntegrityError:
                print(1)
                return render(request, 'game/setprofile.html',{
                    "user": profile_exists(request.session),
                    "message": "The username is already taken"
                })
        else:
            request.session.save()
            print(f"session key: {request.session.session_key}")
            profile = Profile(user_id=request.session.session_key, username=ID, image=image, description=description)
            try:
                profile.save()
            except IntegrityError:
                print(2)
                return render(request, 'game/setprofile.html',{
                    "user": profile_exists(request.session),
                    "message": "The username is already taken"
                })
        return HttpResponseRedirect(reverse("game:profile"))

    #get request
    return render(request, 'game/setprofile.html',{
        "user": profile_exists(request.session)
    })

def profile(request):
    if profile_exists(request.session):
        profile = Profile.objects.get(user_id = request.session.session_key)
        username = profile.username
        description = profile.description
        img_link = profile.image
        print(username, description, img_link)
        return render(request, 'game/profile.html',{
            "user": profile_exists(request.session),
            "username":username,
            "description":description,
            "img_link":img_link
        })
    else:
        return HttpResponseRedirect(reverse("game:setprofile"))

def render_image(request, filename):
    try:
        with open(join(BASE_DIR, "images", filename), "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except FileNotFoundError:
        return HttpResponseNotFound("<h1>Page not found</h1>")


def room(request, room_name):
    if Game.objects.filter(name=room_name).exists():
        game = Game.objects.get(name=room_name)
        if game.full():
            return HttpResponse("<h1>Game is full</h1>", status=409)
        if profile_exists(request.session):
            return render(request, 'game/room.html', {
                'room_name': room_name
            })
        else:
            return HttpResponseRedirect(reverse("game:setprofile"))
    else:
        return HttpResponseNotFound("<h1>Page not found</h1>")

def creategame(request):
    # redirect if profile not set
    if not profile_exists(request.session):
        return HttpResponseRedirect(reverse("game:setprofile"))
    # post request
    if request.method == "POST":
        room_name = request.POST["room-name"]
        max_people = request.POST["max-people"]
        goal_score = request.POST["goal-score"]
        game = Game(name = room_name, max_people = max_people, goal_score = goal_score, state = 0)
        game.save()
        return HttpResponseRedirect(reverse("game:room", args=[room_name]))


    # get request
    return render(request, "game/creategame.html", {
        "user": profile_exists(request.session)
    })