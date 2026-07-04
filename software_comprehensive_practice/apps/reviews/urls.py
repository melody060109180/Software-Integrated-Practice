from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:goods_id>/', views.review_add, name='add'),
    path('list/<int:goods_id>/', views.review_list, name='list'),
    path('delete/<int:pk>/', views.review_delete, name='delete'),
]
