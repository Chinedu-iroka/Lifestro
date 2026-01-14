from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', views.login_register_view, name='login_register'),
    path('logout/', views.logout_view, name='logout'),
    path('book/<int:item_id>/', views.book_item, name='book_item'),
    path('cars/', views.car_list, name='car_list'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
]
