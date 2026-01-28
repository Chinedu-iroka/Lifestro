import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifestro_website.settings')
django.setup()

from django.contrib.auth.models import User

username = 'testuser'
password = 'testpass'

try:
    u = User.objects.get(username=username)
    u.set_password(password)
    u.save()
    print(f"Password reset for {username}")
    print(f"Check password 'testpass': {u.check_password(password)}")
except User.DoesNotExist:
    User.objects.create_user(username=username, password=password)
    print(f"User {username} created")
