from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('', views.favorite_list, name='list'),
    path('toggle/<int:goods_id>/', views.toggle_favorite, name='toggle'),
    path('remove/<int:pk>/', views.remove_favorite, name='remove'),
]
