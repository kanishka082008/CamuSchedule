import os

from django.conf import settings
from django.shortcuts import render, redirect


def home(request):
    default_profile_url = None
    default_path = os.path.join(settings.MEDIA_ROOT, 'default_profile.jpg')
    if os.path.exists(default_path):
        default_profile_url = settings.MEDIA_URL + 'default_profile.jpg'
    return render(request, 'home.html', {'default_profile_url': default_profile_url})


def upload_profile(request):
    """Save uploaded image to the logged-in user's Profile.image or default profile."""
    if request.method == 'POST' and request.FILES.get('image'):
        f = request.FILES['image']
        if request.user.is_authenticated:
            profile = request.user.profile
            profile.image.save(f.name, f, save=True)
        else:
            target_path = os.path.join(settings.MEDIA_ROOT, 'default_profile.jpg')
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            with open(target_path, 'wb+') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
        return redirect('home')
    return render(request, 'upload_profile.html')
