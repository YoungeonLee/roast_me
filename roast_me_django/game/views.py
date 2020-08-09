from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

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
            return HttpResponseRedirect(reverse('games'))
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
        print(request.POST)
        ID = request.POST["InputID"]
        password = request.POST['InputPassword']
        user = authenticate(request, username=ID, password=password)
        if user is not None:
            login(request=request, user=user)
            return HttpResponseRedirect(reverse("index"))
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
