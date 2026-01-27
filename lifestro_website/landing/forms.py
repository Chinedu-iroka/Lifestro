from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import UserProfile, Booking

class ExtendedRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'PASSWORD',
        'class': 'auth-input'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'CONFIRM PASSWORD',
        'class': 'auth-input'
    }))
    
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'FIRST NAME',
        'class': 'auth-input'
    }))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'LAST NAME',
        'class': 'auth-input'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'EMAIL ADDRESS',
        'class': 'auth-input'
    }))
    
    # Profile fields
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'placeholder': 'PHONE NUMBER',
        'class': 'auth-input'
    }))
    address = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'ADDRESS',
        'class': 'auth-input',
        'rows': 3
    }))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={
        'placeholder': 'DATE OF BIRTH (YYYY-MM-DD)',
        'class': 'auth-input',
        'type': 'date'
    }))
    face_photo = forms.ImageField(required=False, label="Face Photo")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'USERNAME', 'class': 'auth-input'}),
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username


class ContactForm(forms.Form):
    name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'YOUR NAME',
        'class': 'auth-input'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'YOUR EMAIL',
        'class': 'auth-input'
    }))
    comment = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'YOUR MESSAGE',
        'class': 'auth-input',
        'rows': 5
    }))


class BookingForm(forms.ModelForm):
    DURATION_CHOICES = [
        ('airport', 'Airport Pick-up / Drop-off'),
        ('10h', '10 Hours'),
        ('12h', '12 Hours'),
        ('More', 'Days'),
        ('custom', 'Custom'),
    ]
    
    duration_type = forms.ChoiceField(
        choices=DURATION_CHOICES, 
        widget=forms.RadioSelect(attrs={'class': 'duration-select'})
    )
    pickup_location = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-input', 
            'placeholder': 'Enter pickup location'
        })
    )
    destination = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-input', 
            'placeholder': 'Enter destination'
        })
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-input',
            'id': 'id_start_date'
        })
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-input',
            'id': 'id_end_date'
        })
    )
    
    # Apartment-specific fields
    number_of_guests = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )
    stay_type = forms.ChoiceField(
        required=False,
        choices=[
            ('normal', 'Normal Stay'),
            ('party', 'Party/Event')
        ],
        widget=forms.RadioSelect()
    )

    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop('item', None)
        super(BookingForm, self).__init__(*args, **kwargs)
        
        if self.item and self.item.category.slug == 'apartments':
            # For apartments, customize the form
            self.fields['duration_type'].choices = [('custom', 'Custom')]
            self.fields['duration_type'].initial = 'custom'
            self.fields['duration_type'].widget = forms.HiddenInput()
            
            # Hide location fields for apartments
            self.fields['pickup_location'].widget = forms.HiddenInput()
            self.fields['destination'].widget = forms.HiddenInput()
            
            # Make end_date required for apartments
            self.fields['end_date'].required = True
            
            # Make apartment-specific fields required
            self.fields['number_of_guests'].required = True
            self.fields['stay_type'].required = True
        else:
            # For non-apartments (cars), hide apartment fields
            self.fields['number_of_guests'].widget = forms.HiddenInput()
            self.fields['stay_type'].widget = forms.HiddenInput()

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        
        # Check if start_date is in the past
        if start_date and start_date < timezone.now().date():
            raise ValidationError("Start date cannot be in the past.")
        
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        
        # For apartments, end_date is required
        if self.item and self.item.category.slug == 'apartments':
            if not end_date:
                raise ValidationError("Check-out date is required for apartment bookings.")
        
        return end_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        duration_type = cleaned_data.get('duration_type')
        
        # Validate dates for apartments
        if self.item and self.item.category.slug == 'apartments':
            if start_date and end_date:
                # Check that end_date is after start_date
                if end_date <= start_date:
                    raise ValidationError("Check-out date must be after check-in date.")
                
                # Check for overlapping bookings
                from django.db.models import Q
                overlapping_bookings = Booking.objects.filter(
                    item=self.item,
                    status__in=['pending', 'confirmed']
                ).filter(
                    Q(start_date__lte=end_date, end_date__gte=start_date)
                )
                
                # Exclude current booking if editing
                if self.instance and self.instance.pk:
                    overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)
                
                if overlapping_bookings.exists():
                    raise ValidationError(
                        "This apartment is already booked for the selected dates. "
                        "Please choose different dates."
                    )
        
        # Validate for custom duration (multi-day car rentals)
        if duration_type == 'custom' and self.item and self.item.category.slug != 'apartments':
            if not end_date:
                raise ValidationError("End date is required for custom duration.")
            if end_date <= start_date:
                raise ValidationError("End date must be after start date.")
        
        return cleaned_data

    class Meta:
        model = Booking
        fields = [
            'duration_type', 
            'pickup_location', 
            'destination', 
            'start_date', 
            'end_date',
            'number_of_guests',
            'stay_type'
        ]