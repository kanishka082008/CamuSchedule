from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.core.files import File
from django.conf import settings
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Assign a local image file to a user profile. Usage: python manage.py assign_profile_image /path/to/image.jpg username [--create-user]'

    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str, help='Local path to image file')
        parser.add_argument('username', type=str, help='Username to assign the image to')
        parser.add_argument('--create-user', action='store_true', help='Create the user if it does not exist (password will be "password")')
        parser.add_argument('--dest-filename', type=str, help='Destination filename to save in media/profiles (e.g. kanishka.jpg)')

    def handle(self, *args, **options):
        filepath = options['filepath']
        username = options['username']
        create_user = options['create_user']

        if not os.path.exists(filepath):
            raise CommandError(f'File not found: {filepath}')

        user = User.objects.filter(username=username).first()
        if not user:
            if create_user:
                user = User.objects.create_user(username=username, password='password')
                self.stdout.write(self.style.SUCCESS(f'Created user "{username}" with password "password"'))
            else:
                raise CommandError(f'User "{username}" does not exist. Use --create-user to create it.')

        # Ensure profile exists
        profile = None
        try:
            profile = user.profile
        except Exception:
            # try to create a profile if model exists
            from camu.models import Profile
            profile = Profile.objects.create(user=user)

        # Save file into profile.image; allow custom destination filename
        dest_filename = options.get('dest_filename')
        with open(filepath, 'rb') as f:
            django_file = File(f)
            if dest_filename:
                filename = dest_filename
            else:
                filename = os.path.basename(filepath)
            profile.image.save(filename, django_file, save=True)

        self.stdout.write(self.style.SUCCESS(f'Assigned image {filename} to user {username}'))
