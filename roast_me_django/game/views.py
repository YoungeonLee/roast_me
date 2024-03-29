from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django import forms
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from .models import Profile, Game, Player, Message
from pathlib import Path
from os.path import join
from PIL import Image, UnidentifiedImageError
from django.core.files.uploadedfile import InMemoryUploadedFile
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
from django.contrib.sessions.models import Session


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
    # if need to make profile
    if not profile_exists(request.session):
        return HttpResponseRedirect(reverse("game:setprofile"))
    if request.method == "POST":
        print(request.POST)
        game_name = request.POST["gameName"]
        game_list = Game.objects.filter(name__icontains=game_name)
    else:   
        game_list = Game.objects.all()
        game_name = ""

    return render(request, "game/games.html", {
        "user": profile_exists(request.session),
        "games": game_list,
        "game_name": game_name
    })

    
def setprofile(request):
    # post request
    if request.method == "POST":
        #print(request.POST)
        try:
            # check if all forms are valid
            ID = request.POST["InputID"]
            image = request.FILES['profileImage']
            print(image)
            print(type(image))
            description = request.POST["description"]
        except Exception as e:
            print(e)
            return render(request, 'game/setprofile.html',{
                    "user": profile_exists(request.session),
                    "message": "Server Error; make sure you filled the entire form correctly",
                    "description": description,
                    "username": ID
                })
        
        try:
            # check if image is valid and resize
            print("opening image")
            img = Image.open(image)
            
        except UnidentifiedImageError:
            return render(request, 'game/setprofile.html',{
                    "user": profile_exists(request.session),
                    "message": "Invalid image",
                    "description": description,
                    "username": ID
                })

            
        if profile_exists(request.session):
            profile = Profile.objects.get(user_id=request.session.session_key)
            if Player.objects.filter(user=profile).exists():
                print("set profile: session already has a player")
                return render(request, 'game/setprofile.html',{
                        "user": profile_exists(request.session),
                        "message": "You seem to be in game currently. Exit out of all games to reset profile.",
                        "description": description,
                        "username": ID
                    })
            print(2)
            profile = Profile.objects.get(user_id=request.session.session_key)
            profile.username = ID
            profile.image = image
            profile.description = description
            try:
                profile.save()
            except IntegrityError as e:
                # delete image !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                print(e)
                return render(request, 'game/setprofile.html',{
                    "user": profile_exists(request.session),
                    "message": "The username is already taken",
                    "description": description,
                    "username": ID
                })
        else:
            print(3)
            print(request.session)
            print(request.session.session_key)
            if not Session.objects.filter(pk=request.session.session_key).exists():
                request.session.create()
            profile = Profile(user_id=request.session.session_key, username=ID, image=image, description=description)
            try:
                profile.save()
            except IntegrityError as e:
                print(e)
                return render(request, 'game/setprofile.html',{
                    "user": profile_exists(request.session),
                    "message": "The username is already taken",
                    "description": description,
                    "username": ID
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

def static(request, app, filename):
    try:
        with open(join(BASE_DIR, "static", app, filename), "rb") as f:
            return HttpResponse(f.read(), content_type="image/png")
    except FileNotFoundError:
        return HttpResponseNotFound("<h1>Page not found</h1>")

def room(request, room_name):
    if Game.objects.filter(name=room_name).exists():
        game = Game.objects.get(name=room_name)
        if game.full():
            return HttpResponse("<h1>Game is full</h1>", status=409)
        if profile_exists(request.session):
            profile = Profile.objects.get(user_id=request.session.session_key)
            if game.player.filter(user=profile).exists():
                return HttpResponse("You are already in game. Check your other tabs", status=409)
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
        timer = request.POST["timer"]
        if Game.objects.filter(name=room_name).exists():
            return render(request, "game/creategame.html", {
            "user": profile_exists(request.session),
            "message": "Game name taken. Pick a different name!",
            "room_name": room_name,
            "max_people": max_people,
            "goal_score": goal_score,
            "timer" : timer
        })
        game = Game(name = room_name, max_people = max_people, goal_score = goal_score, state = 0, round_length=timer)
        game.save()
        return HttpResponseRedirect(reverse("game:room", args=[room_name]))


    # get request
    return render(request, "game/creategame.html", {
        "user": profile_exists(request.session)
    })

def support(request):
    if request.method == "POST":
        content = request.POST["content"]
        message = Message(content=content)
        message.save()
        return render(request, "game/support.html", {
            "user": profile_exists(request.session),
            "message": "Submitted"
        })
    return render(request, "game/support.html", {
        "user": profile_exists(request.session)
    })

