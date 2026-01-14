from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import RentalItem, Category, Booking
from django.utils import timezone
import datetime

def index(request):
    cars = RentalItem.objects.filter(category__slug='cars')
    apts = RentalItem.objects.filter(category__slug='apartments')
    return render(request, 'landing/index.html', {'cars': cars, 'apts': apts})

def car_list(request):
    cars = RentalItem.objects.filter(category__slug='cars')
    return render(request, 'landing/car_list.html', {'cars': cars})

def item_detail(request, pk):
    item = get_object_or_404(RentalItem, pk=pk)
    youtube_id = None
    if item.video_url:
        if 'youtube.com' in item.video_url:
            if 'v=' in item.video_url:
                youtube_id = item.video_url.split('v=')[1].split('&')[0]
        elif 'youtu.be' in item.video_url:
            youtube_id = item.video_url.split('/')[-1]
            
    return render(request, 'landing/item_detail.html', {
        'item': item,
        'youtube_id': youtube_id
    })

def login_register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Simple logic to handle both login and register
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
        else:
            # Try to register if user doesn't exist
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                messages.success(request, f"Account created for {username}!")
            else:
                messages.error(request, "Invalid credentials.")
        
    return redirect('index')

def logout_view(request):
    logout(request)
    return redirect('index')

def book_item(request, item_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to book an item.")
        return redirect('index')
    
    if request.method == 'POST':
        item = RentalItem.objects.get(id=item_id)
        # For simplicity in this MVP, we book for today + 1 day
        start_date = timezone.now().date()
        end_date = start_date + datetime.timedelta(days=1)
        
        Booking.objects.create(
            user=request.user,
            item=item,
            start_date=start_date,
            end_date=end_date
        )
        messages.success(request, f"Successfully booked {item.name}!")
        
    return redirect('index')
