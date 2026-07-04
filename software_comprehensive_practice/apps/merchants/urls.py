from django.urls import path
from . import views

app_name = 'merchants'

urlpatterns = [
    path('register/', views.merchant_register, name='register'),
    path('login/', views.merchant_login, name='login'),
    path('logout/', views.merchant_logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('goods/', views.goods_list, name='goods_list'),
    path('goods/add/', views.goods_add, name='goods_add'),
    path('goods/<int:pk>/edit/', views.goods_edit, name='goods_edit'),
    path('goods/<int:pk>/delete/', views.goods_delete, name='goods_delete'),
    path('goods/<int:pk>/toggle/', views.goods_toggle, name='goods_toggle'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/ship/', views.order_ship, name='order_ship'),
]
