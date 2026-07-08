from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    # 数据统计
    path('', views.dashboard, name='dashboard'),
    
    # 用户管理
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    
    # 商家管理
    path('merchants/', views.merchant_list, name='merchant_list'),
    path('merchants/<int:pk>/', views.merchant_detail, name='merchant_detail'),
    
    # 商品管理
    path('goods/', views.goods_list, name='goods_list'),
    path('goods/<int:pk>/', views.goods_detail, name='goods_detail'),
    
    # 订单管理
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    
    # 系统设置
    path('settings/', views.settings_view, name='settings'),
]
