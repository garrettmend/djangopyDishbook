from django.shortcuts import render
from . import models
# Create your views here.
def index(request):
    return render(request, "index.html", { })

def recipe(request, recipe_id):
    return render(request, "recipe.html", {"recipe_id": recipe_id})

def search(request):
    return render(request, "search.html", {})

def profile(request, username):
    return render(request, "profile.html", {"username": username})

def signin(request):
    return render(request, "signin.html", {})