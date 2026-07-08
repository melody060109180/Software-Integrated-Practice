from django.urls import path
from . import views

app_name = 'riders'

urlpatterns = [
    path('register/', views.rider_register, name='register'),
    path('logout/', views.rider_logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('deliveries/', views.delivery_list, name='delivery_list'),
    path('deliveries/<int:pk>/', views.delivery_detail, name='delivery_detail'),
    path('deliveries/<int:pk>/accept/', views.accept_delivery, name='accept_delivery'),
    path('deliveries/<int:pk>/complete/', views.complete_delivery, name='complete_delivery'),
    path('history/', views.delivery_history, name='history'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]
