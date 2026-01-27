from django.contrib import admin
from django.utils.html import format_html
from .models import Category, RentalItem, Booking, RentalImage, UserProfile

class RentalImageInline(admin.TabularInline):
    model = RentalImage
    extra = 3
    fields = ('image', 'caption')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'item_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Number of Items'

@admin.register(RentalItem)
class RentalItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_per_day', 'rating', 'is_featured', 'image_preview')
    list_filter = ('category', 'is_featured', 'rating')
    search_fields = ('name', 'description')
    list_editable = ('is_featured', 'rating')
    inlines = [RentalImageInline]
    readonly_fields = ('image_preview',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'description')
        }),
        ('Pricing & Rating', {
            'fields': ('price_per_day', 'rating', 'is_featured')
        }),
        ('Media', {
            'fields': ('image', 'image_preview', 'video_url')
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 300px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'user', 
        'item', 
        'item_category',
        'start_date', 
        'end_date', 
        'status_badge',
        'total_cost',
        'created_at'
    ]
    list_filter = [
        'status', 
        'item__category', 
        'start_date',
        'created_at',
        'stay_type'
    ]
    search_fields = [
        'user__username', 
        'user__email',
        'item__name',
        'pickup_location',
        'destination'
    ]
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at', 'total_cost']
    list_per_page = 25
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'item', 'status', 'start_date', 'end_date')
        }),
        ('Car Rental Details', {
            'fields': ('duration_type', 'pickup_location', 'destination'),
            'classes': ('collapse',),
            'description': 'These fields apply to car rentals only'
        }),
        ('Apartment Details', {
            'fields': ('number_of_guests', 'stay_type'),
            'classes': ('collapse',),
            'description': 'These fields apply to apartment bookings only'
        }),
        ('Cost & Timestamps', {
            'fields': ('total_cost', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_cancelled', 'mark_as_completed', 'mark_as_pending']
    
    def item_category(self, obj):
        return obj.item.category.name
    item_category.short_description = 'Category'
    item_category.admin_order_field = 'item__category__name'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'confirmed': '#28A745',
            'cancelled': '#DC3545',
            'completed': '#6C757D'
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def total_cost(self, obj):
        cost = obj.get_total_cost()
        return format_html('₦{}</ span>', f'{cost:,.2f}')
    total_cost.short_description = 'Total Cost'
    
    # Admin actions
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} booking(s) marked as Confirmed.')
    mark_as_confirmed.short_description = "✓ Mark as Confirmed"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} booking(s) marked as Cancelled.')
    mark_as_cancelled.short_description = "✗ Mark as Cancelled"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} booking(s) marked as Completed.')
    mark_as_completed.short_description = "✓ Mark as Completed"
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} booking(s) marked as Pending.')
    mark_as_pending.short_description = "⏳ Mark as Pending"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'date_of_birth', 'has_photo', 'total_bookings')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('date_of_birth',)
    readonly_fields = ('photo_preview', 'total_bookings', 'recent_bookings')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'address')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'face_photo', 'photo_preview')
        }),
        ('Booking Statistics', {
            'fields': ('total_bookings', 'recent_bookings'),
            'classes': ('collapse',)
        }),
    )
    
    def has_photo(self, obj):
        if obj.face_photo:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_photo.short_description = 'Photo'
    
    def photo_preview(self, obj):
        if obj.face_photo:
            return format_html('<img src="{}" style="max-height: 150px; border-radius: 50%;" />', obj.face_photo.url)
        return "No Photo"
    photo_preview.short_description = 'Photo Preview'
    
    def total_bookings(self, obj):
        count = obj.user.bookings.count()
        return format_html('<strong>{}</strong> booking(s)', count)
    total_bookings.short_description = 'Total Bookings'
    
    def recent_bookings(self, obj):
        bookings = obj.user.bookings.order_by('-created_at')[:5]
        if not bookings:
            return "No bookings yet"
        
        html = '<ul style="margin: 0; padding-left: 20px;">'
        for booking in bookings:
            html += f'<li>{booking.item.name} - {booking.start_date} ({booking.get_status_display()})</li>'
        html += '</ul>'
        return format_html(html)
    recent_bookings.short_description = 'Recent Bookings'