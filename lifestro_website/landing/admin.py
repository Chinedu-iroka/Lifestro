from django.contrib import admin
from .models import Category, RentalItem, Booking, RentalImage

class RentalImageInline(admin.TabularInline):
    model = RentalImage
    extra = 3

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(RentalItem)
class RentalItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_per_day', 'rating', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'description')
    inlines = [RentalImageInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
