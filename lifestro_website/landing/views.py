from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import RentalItem, Category, UserProfile, Booking
from .forms import ExtendedRegistrationForm
from django.utils import timezone
import datetime

def index(request):
    cars = RentalItem.objects.filter(category__slug='cars', is_featured=True)
    apartments = RentalItem.objects.filter(category__slug='apartments', is_featured=True)
    return render(request, 'landing/index.html', {
        'cars': cars,
        'apartments': apartments
    })

def car_list(request):
    cars = RentalItem.objects.filter(category__slug='cars')
    return render(request, 'landing/car_list.html', {'cars': cars})

def boat_list(request):
    boats = RentalItem.objects.filter(category__slug='boats')
    return render(request, 'landing/boat_list.html', {'boats': boats})

def apartment_list(request):
    apartments = RentalItem.objects.filter(category__slug='apartments')
    return render(request, 'landing/apartment_list.html', {'apartments': apartments})

def jet_list(request):
    jets = RentalItem.objects.filter(category__slug='private-jets')
    return render(request, 'landing/jet_list.html', {'jets': jets})

def hotel_list(request):
    hotels = RentalItem.objects.filter(category__slug='hotels')
    return render(request, 'landing/hotel_list.html', {'hotels': hotels})

def about_us(request):
    return render(request, 'landing/about_us.html')

from .forms import ExtendedRegistrationForm, ContactForm

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data (e.g., send email)
            # For now, we'll just render the page with a success message
            return render(request, 'landing/contact_us.html', {'form': ContactForm(), 'success': True})
    else:
        form = ContactForm()
    return render(request, 'landing/contact_us.html', {'form': form})

def partner_with_us(request):
    return render(request, 'landing/partner_with_us.html')

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
        
        if not username or not password:
            messages.error(request, "Both username and password are required.")
            return redirect('index')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('index')
        else:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Incorrect password for this account.")
                return redirect('index')
            
            # User doesn't exist, try to create
            try:
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                messages.success(request, f"Account created for {username}!")
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
            return redirect('index')
        
    return redirect('index')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        form = ExtendedRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create User
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )
                
                # Create UserProfile
                UserProfile.objects.create(
                    user=user,
                    phone_number=form.cleaned_data['phone_number'],
                    address=form.cleaned_data['address'],
                    date_of_birth=form.cleaned_data['date_of_birth'],
                    face_photo=form.cleaned_data['face_photo']
                )
                
                # Login the user
                login(request, user)
                messages.success(request, f"Welcome to Lifestro, {user.first_name}! Your account has been created.")
                return redirect('index')
            except Exception as e:
                messages.error(request, f"An error occurred during registration: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = ExtendedRegistrationForm()
        
    return render(request, 'landing/register.html', {'form': form})

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

def team_list(request):
    team_members = [
        {
            'name': 'Alexander Sterling',
            'role': 'Founder & CEO',
            'bio': 'Visionary leader with 15 years in luxury hospitality and asset management.',
            'image': 'hero.png' # Placeholder
        },
        {
            'name': 'Elena Vance',
            'role': 'Chief Operations Officer',
            'bio': 'Ensuring seamless execution of every extraordinary journey.',
            'image': 'ocean-view-villa.png' # Placeholder
        },
        {
            'name': 'Marcus Thorne',
            'role': 'Head of Concierge',
            'bio': 'Curating bespoke experiences for our most discerning clients.',
            'image': 'sports-car.png' # Placeholder
        },
        {
            'name': 'Isabella Ricci',
            'role': 'Lead Interior Designer',
            'bio': 'Defining the aesthetic of our exclusive property portfolio.',
            'image': 'ocean-view-villa.png' # Placeholder
        }
    ]
    return render(request, 'landing/team_list.html', {'team_members': team_members})

def partners_list(request):
    corporate_partners = [
        {'name': 'Global Jets Inc', 'description': 'Premier Private Aviation', 'image': 'hero.png'},
        {'name': 'Elite Estates', 'description': 'Luxury Property Management', 'image': 'ocean-view-villa.png'},
        {'name': 'Velocity Exotics', 'description': 'Supercar Fleet Services', 'image': 'sports-car.png'},
        {'name': 'Nautical Ventures', 'description': 'Exclusive Yacht Charting', 'image': 'ocean-view-villa.png'},
    ]
    
    luxury_brands = [
        {'name': 'Aurum Timepieces', 'description': 'Horological Excellence', 'image': 'hero.png'},
        {'name': 'Velluto Interiors', 'description': 'Italian Design House', 'image': 'ocean-view-villa.png'},
        {'name': 'Apex Security', 'description': 'Private Client Protection', 'image': 'sports-car.png'},
        {'name': 'Savour Culinary', 'description': 'Michelin Star Dining', 'image': 'ocean-view-villa.png'},
    ]
    
    return render(request, 'landing/partners_list.html', {
        'corporate_partners': corporate_partners,
        'luxury_brands': luxury_brands
    })
