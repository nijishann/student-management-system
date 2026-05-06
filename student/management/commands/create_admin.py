from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Create default admin user'

    def handle(self, *args, **kwargs):
        # Railway এর existing variables ব্যবহার করছি
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@gmail.com')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                password=password,
                email=email
            )
            self.stdout.write(f'✅ Admin created: {username}')
        else:
            self.stdout.write(f'ℹ️ Admin already exists: {username}')