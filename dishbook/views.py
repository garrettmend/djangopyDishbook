from django.shortcuts import render
from . import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
# Create your views here.
def index(request):
    recipes = models.Recipe.objects.order_by('-id')[:3]
    return render(request, "index.html", {"recipes":  recipes})

def recipe(request, recipe_id):
    recipe = get_object_or_404(models.Recipe, id=recipe_id)
    variations_count = models.Recipe.objects.filter(copied_from=recipe).count()
    #splice input string [0][1][rest] key : ingr val : amount
import re

def recipe(request, recipe_id):
    recipe = get_object_or_404(models.Recipe, id=recipe_id)
    variations_count = models.Recipe.objects.filter(copied_from=recipe).count()

def recipe(request, recipe_id):
    recipe = get_object_or_404(models.Recipe, id=recipe_id)
    variations_count = models.Recipe.objects.filter(copied_from=recipe).count()

    ingr = {} 

    for step in recipe.steps.all().order_by('order'):
        for ingredient in step.ingredients.all():
            key = ingredient.name.strip()
            val = (ingredient.amount, ingredient.unit.strip())

            if key not in ingr:
                ingr[key] = [val]
            else:
                for idx, t in enumerate(ingr[key]):
                    if t[1] == val[1]:
                        ingr[key][idx] = (t[0] + val[0], t[1])
                        break
                else:
                    ingr[key].append(val)


        
    return render(request, "recipe.html", {"recipe_id": recipe_id, "recipe": recipe, "page_title": recipe.title, "variations_count": variations_count, "ingr":ingr})

def search(request):
    q = request.GET.get('q', '').strip()
    recipes = models.Recipe.objects.all()
    if q:
        # tag search: tag:name
        if q.lower().startswith('tag:'):
            tag = q.split(':', 1)[1].strip()
            recipes = models.Recipe.objects.filter(tags__name__iexact=tag).distinct()
        elif q.lower().startswith('author:'):
            author = q.split(':', 1)[1].strip()
            recipes = models.Recipe.objects.filter(author__username__iexact=author)
        else:
            recipes = models.Recipe.objects.filter(
                models.Q(title__icontains=q) |
                models.Q(description__icontains=q) |
                models.Q(tags__name__icontains=q)
            ).distinct()
    return render(request, "search.html", {"recipes":recipes, "q": q})

def profile(request, username):
    author = get_object_or_404(User, username=username)
    recipes = models.Recipe.objects.filter(author=author)
    return render(request, "profile.html", {"username": username, "author": author, "recipes": recipes})

def signin(request):
    return render(request, "signin.html", {})