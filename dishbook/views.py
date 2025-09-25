from django.shortcuts import render
from . import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
# Create your views here.
def index(request):
    recipes = models.Recipe.objects.order_by('-id')[:3]
    return render(request, "index.html", {"recipes":  recipes})

def recipe(request, recipe_id):
    return render(request, "recipe.html", {"recipe_id": recipe_id})

def search(request):
    recipes = models.Recipe.objects.all()
    return render(request, "search.html", {"recipes":recipes})

def profile(request, username):
    author = get_object_or_404(User, username=username)
    recipes = models.Recipe.objects.filter(author=author)
    return render(request, "profile.html", {"username": username, "author": author, "recipes": recipes})

def signin(request):
    return render(request, "signin.html", {})