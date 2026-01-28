import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifestro_website.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

# Ensure user exists
username = 'testuser'
password = 'testpass'
if not User.objects.filter(username=username).exists():
    User.objects.create_user(username=username, password=password)
    print(f"User {username} created.")
else:
    print(f"User {username} already exists.")

c = Client()

# Test Login
login_url = reverse('login_register')
print(f"Testing login at {login_url}")
response = c.post(login_url, {'username': username, 'password': password})
print(f"Login Response Code: {response.status_code}")
if response.status_code == 302:
    print(f"Redirects to: {response.url}")
else:
    print(f"Response Content: {response.content}")

# Check if session has user
if '_auth_user_id' in c.session:
    print("Login SUCCESS: User session found.")
else:
    print("Login FAILED: No user session.")

# Test Logout
logout_url = reverse('logout')
print(f"Testing logout at {logout_url}")
response = c.get(logout_url)
print(f"Logout Response Code: {response.status_code}")
if response.status_code == 302:
    print(f"Redirects to: {response.url}")

# Check session
if '_auth_user_id' not in c.session:
    print("Logout SUCCESS: User session cleared.")
else:
    print("Logout FAILED: User session still exists.")
