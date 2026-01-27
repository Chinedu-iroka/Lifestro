from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class RentalItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    image = models.ImageField(upload_to='rentals/')
    video_url = models.URLField(blank=True, null=True, help_text="Link to YouTube or Vimeo video")
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class RentalImage(models.Model):
    item = models.ForeignKey(RentalItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rentals/gallery/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.item.name}"

class Booking(models.Model):
    # Status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    # Duration choices
    DURATION_CHOICES = [
        ('airport', 'Airport Pick-up / Drop-off'),
        ('10h', '10 Hours'),
        ('12h', '12 Hours'),
        ('More', 'Days'),
        ('custom', 'Select Return Date'),
    ]
    
    # Stay type choices (for apartments)
    STAY_TYPE_CHOICES = [
        ('normal', 'Normal Stay'),
        ('party', 'Party/Event'),
    ]
    
    # Core booking fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    item = models.ForeignKey(RentalItem, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Car rental specific fields
    pickup_location = models.CharField(max_length=255, blank=True, null=True)
    destination = models.CharField(max_length=255, blank=True, null=True)
    duration_type = models.CharField(max_length=20, choices=DURATION_CHOICES, default='airport')
    
    # Apartment specific fields
    number_of_guests = models.IntegerField(blank=True, null=True, help_text="Number of guests for apartment bookings")
    stay_type = models.CharField(
        max_length=20, 
        choices=STAY_TYPE_CHOICES, 
        blank=True, 
        null=True,
        help_text="Type of stay for apartment bookings"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['item', 'start_date', 'end_date']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.item.name} ({self.start_date})"
    
    def get_total_nights(self):
        """Calculate total nights for apartment bookings"""
        if self.end_date and self.start_date:
            return (self.end_date - self.start_date).days
        return 0
    
    def get_total_cost(self):
        """Calculate total cost based on rental type"""
        if self.item.category.slug == 'apartments' and self.end_date:
            nights = self.get_total_nights()
            return nights * self.item.price_per_day
        elif self.duration_type == 'More' or self.duration_type == 'custom':
            if self.end_date:
                days = (self.end_date - self.start_date).days
                return days * self.item.price_per_day
        # For hourly/airport rentals, return base price
        return self.item.price_per_day
    
    def is_overlapping(self, start_date, end_date):
        """Check if this booking overlaps with given date range"""
        if not self.end_date:
            return False
        return (
            (start_date <= self.end_date) and 
            (end_date >= self.start_date)
        )

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    face_photo = models.ImageField(upload_to='profiles/faces/', null=True, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"