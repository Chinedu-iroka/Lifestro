from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', views.login_register_view, name='login_register'),
    path('logout/', views.logout_view, name='logout'),
    path('book/<int:item_id>/', views.book_item, name='book_item'),
    path('cars/', views.car_list, name='car_list'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('register/', views.register_view, name='register'),
    path('boats/', views.boat_list, name='boat_list'),
    path('apartments/', views.apartment_list, name='apartment_list'),
    path('jets/', views.jet_list, name='jet_list'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('teams/', views.team_list, name='team_list'),
    path('partner/', views.partner_with_us, name='partner_with_us'),
    path('partners/', views.partners_list, name='partners_list'),
    path('profile/', views.profile_view, name='profile'),
]
