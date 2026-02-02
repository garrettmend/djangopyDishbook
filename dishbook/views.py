from django.shortcuts import render
from . import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
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
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(tags__name__icontains=q)
            ).distinct()
    return render(request, "search.html", {"recipes":recipes, "q": q})

def profile(request, username):
    author = get_object_or_404(User, username=username)
    recipes = models.Recipe.objects.filter(author=author)
    return render(request, "profile.html", {"username": username, "author": author, "recipes": recipes})

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect


def signin(request):
    if request.method == 'POST':
        identifier = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        username = identifier
        # If user submitted an email, try to resolve to username
        if '@' in identifier:
            try:
                u = User.objects.get(email__iexact=identifier)
                username = u.username
            except User.DoesNotExist:
                # leave username as identifier (authenticate will fail)
                username = identifier
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'signin.html', { 'error': 'Invalid username/email or password', 'page_title': 'Sign in' })
    return render(request, "signin.html", { 'page_title': 'Sign in' })

from django.http import FileResponse, Http404
import mimetypes
from django.conf import settings


def recipe_photo(request, recipe_id):
    recipe = get_object_or_404(models.Recipe, id=recipe_id)
    if not recipe.photo:
        # Serve default recipe image from static
        static_path = settings.BASE_DIR / 'static' / 'recipe.png'
        if static_path.exists():
            return FileResponse(open(static_path, 'rb'), content_type='image/png')
        raise Http404("No photo")
    try:
        recipe.photo.open('rb')
        content_type = mimetypes.guess_type(recipe.photo.name)[0] or 'application/octet-stream'
        return FileResponse(recipe.photo, content_type=content_type)
    except Exception:
        raise Http404("Error opening photo")


def profile_photo(request, username):
    user = get_object_or_404(User, username=username)
    profile = getattr(user, 'profile', None)
    if profile and profile.photo:
        try:
            profile.photo.open('rb')
            content_type = mimetypes.guess_type(profile.photo.name)[0] or 'application/octet-stream'
            return FileResponse(profile.photo, content_type=content_type)
        except Exception:
            raise Http404("Error opening profile photo")
    # Fallback to static profile image
    static_path = settings.BASE_DIR / 'static' / 'profile.png'
    if static_path.exists():
        return FileResponse(open(static_path, 'rb'), content_type='image/png')
    raise Http404("No profile photo")