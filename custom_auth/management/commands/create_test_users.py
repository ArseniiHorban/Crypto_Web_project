#This script creates test users and admin on server start

from django.core.management.base import BaseCommand
from custom_auth.models import User

class Command(BaseCommand):
    help = 'Creates test user and admin on server start'

    def handle(self, *args, **kwargs):
        # Create user
        if not User.objects.filter(username='testuser').exists():
            User.objects.create_user(
                username='testuser',
                email='testuser@example.com',
                password='test123'
            )
            self.stdout.write(self.style.SUCCESS('Test user created: testuser / test123'))

        # Create admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Admin created: admin / admin123'))