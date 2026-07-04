from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('create/', views.create_order, name='create'),
    path('', views.order_list, name='list'),
    path('<int:pk>/', views.order_detail, name='detail'),
    path('<int:pk>/cancel/', views.order_cancel, name='cancel'),
    path('<int:pk>/confirm/', views.order_confirm, name='confirm'),
]
