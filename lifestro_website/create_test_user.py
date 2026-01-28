import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifestro_website.settings')
django.setup()

from django.contrib.auth.models import User

username = 'testuser'
password = 'testpass'

if not User.objects.filter(username=username).exists():
    User.objects.create_user(username=username, password=password)
    print(f"User {username} created.")
else:
    print(f"User {username} already exists.")
