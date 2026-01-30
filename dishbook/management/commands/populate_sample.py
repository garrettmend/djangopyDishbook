from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone
import random
import io
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings
from django.core.files import File

from dishbook.models import Tag, Profile, Recipe, Step, Ingredient


def make_image(text, size=(800, 600), bgcolor=(200, 200, 200)):
    img = Image.new('RGB', size, color=bgcolor)
    draw = ImageDraw.Draw(img)
    # Simple text placement; use default font
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    w, h = draw.textsize(text, font=font)
    draw.text(((size[0]-w)/2, (size[1]-h)/2), text, fill=(0,0,0), font=font)
    bio = io.BytesIO()
    img.save(bio, 'JPEG')
    bio.seek(0)
    return ContentFile(bio.read())


def find_existing_images():
    """Return a list of absolute image file paths found in MEDIA_ROOT and static dirs."""
    images = []
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if media_root and os.path.isdir(media_root):
        for fn in os.listdir(media_root):
            if fn.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(os.path.join(media_root, fn))
    # check static dirs
    sdirs = getattr(settings, 'STATICFILES_DIRS', [])
    for sd in sdirs:
        sd_path = sd
        if isinstance(sd_path, (str,)) and os.path.isdir(sd_path):
            for fn in os.listdir(sd_path):
                if fn.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    images.append(os.path.join(sd_path, fn))
    # Also check repo 'assets' folder
    assets_dir = os.path.join(settings.BASE_DIR, 'assets')
    if os.path.isdir(assets_dir):
        for fn in os.listdir(assets_dir):
            if fn.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(os.path.join(assets_dir, fn))
    return images


class Command(BaseCommand):
    help = 'Populate sample data: tags, users, recipes with photos and profiles.'

    def add_arguments(self, parser):
        parser.add_argument('--tags', type=int, default=10)
        parser.add_argument('--users', type=int, default=10)
        parser.add_argument('--recipes', type=int, default=10)

    def handle(self, *args, **options):
        tags_n = options['tags']
        users_n = options['users']
        recipes_n = options['recipes']

        # Create tags
        tags = []
        for i in range(1, tags_n+1):
            name = f'tag{i}'
            t, _ = Tag.objects.get_or_create(name=name)
            tags.append(t)
        self.stdout.write(self.style.SUCCESS(f'Created/verified {len(tags)} tags'))

        # Find existing images to use for profiles and recipes
        existing_images = find_existing_images()
        random.shuffle(existing_images)

        # Create users and profiles
        users = []
        for i in range(1, users_n+1):
            username = f'user{i}'
            if User.objects.filter(username=username).exists():
                u = User.objects.get(username=username)
            else:
                u = User.objects.create_user(username=username, email=f'{username}@example.com', password='password')
                u.first_name = f'User{i}'
                u.last_name = 'Sample'
                u.save()
            profile, _ = Profile.objects.get_or_create(user=u)
            # Use existing image if available, otherwise generate
            if existing_images:
                img_path = existing_images.pop(0)
                with open(img_path, 'rb') as f:
                    profile.photo.save(os.path.basename(img_path), File(f), save=True)
            else:
                img_content = make_image(f'Profile {i}', size=(400,400))
                profile.photo.save(f'profile_{i}.jpg', img_content, save=True)
            profile.bio = f'This is sample bio for {username}.'
            profile.save()
            users.append(u)
        self.stdout.write(self.style.SUCCESS(f'Created/verified {len(users)} users and profiles'))

        # Create recipes (with photos, steps, ingredients, tags)
        for i in range(1, recipes_n+1):
            title = f'Sample Recipe {i}'
            author = users[(i-1) % len(users)]
            recipe = Recipe.objects.create(
                title=title,
                author=author,
                description=f'Description for {title}',
                prep_time_minutes=random.randint(5,30),
                cook_time_minutes=random.randint(5,90),
                serves=random.randint(1,8),
            )
            # photo: use existing image if available
            if existing_images:
                img_path = existing_images.pop(0)
                with open(img_path, 'rb') as f:
                    recipe.photo.save(os.path.basename(img_path), File(f), save=True)
            else:
                img_content = make_image(f'Recipe {i}', size=(800,600))
                recipe.photo.save(f'recipe_{i}.jpg', img_content, save=True)

            # tags: random 1-3 tags
            sample_tags = random.sample(tags, k=random.randint(1, min(3, len(tags))))
            recipe.tags.set(sample_tags)

            # steps and ingredients (3 steps)
            for s in range(1,4):
                step = Step.objects.create(recipe=recipe, order=s, description=f'Step {s} for {title}')
                # add 1-2 ingredients
                for ing_i in range(random.randint(1,2)):
                    Ingredient.objects.create(step=step, amount=1.0, unit='unit', name=f'Ingredient {s}-{ing_i+1}')

        self.stdout.write(self.style.SUCCESS(f'Created {recipes_n} sample recipes (with photos).'))
        self.stdout.write(self.style.SUCCESS('Done.'))
