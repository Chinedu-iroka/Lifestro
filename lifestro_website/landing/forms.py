from django import core, forms
from django.contrib.auth.models import User
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
        ('airport', 'Airport Drop-off'),
        ('6h', '6 Hours'),
        ('12h', '12 Hours'),
        ('custom', 'Custom'),
    ]
    
    duration_type = forms.ChoiceField(choices=DURATION_CHOICES, widget=forms.RadioSelect(attrs={'class': 'duration-select'}))
    pickup_location = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter pickup location'}))
    destination = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter destination'}))
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})) # Optional, only for custom

    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop('item', None)
        super(BookingForm, self).__init__(*args, **kwargs)
        
        if self.item and self.item.category.slug == 'apartments':
            # Hide/Disable unnecessary fields for apartments
            self.fields['duration_type'].choices = [('custom', 'Custom')]
            self.fields['duration_type'].initial = 'custom'
            self.fields['duration_type'].widget = forms.HiddenInput()
            
            # Make sure location fields are not required
            self.fields['pickup_location'].widget = forms.HiddenInput()
            self.fields['destination'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        pickup = cleaned_data.get('pickup_location')
        dest = cleaned_data.get('destination')
        
        if self.item and self.item.category.slug != 'apartments':
            # For non-apartments (like cars), these might be required or default
            pass # Validation logic if needed 
            
        return cleaned_data

    class Meta:
        model = Booking
        fields = ['duration_type', 'pickup_location', 'destination', 'start_date', 'end_date']
