import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifestro_website.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

username = 'testuser'
password = 'testpass'

try:
    u = User.objects.get(username=username)
    print(f"User found: {u.username}")
    print(f"Has usable password: {u.has_usable_password()}")
    print(f"Check password 'testpass': {u.check_password(password)}")
    print(f"Is active: {u.is_active}")
except User.DoesNotExist:
    print("User does not exist!")

# ... rest of the script is less relevant if check_password fails
