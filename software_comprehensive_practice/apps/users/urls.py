from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('login/unified/', views.unified_login, name='unified_login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('password/', views.password_change, name='password_change'),
    path('address/', views.address_list, name='address_list'),
    path('address/add/', views.address_add, name='address_add'),
    path('address/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('address/<int:pk>/delete/', views.address_delete, name='address_delete'),
]
