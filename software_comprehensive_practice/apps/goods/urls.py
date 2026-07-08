from django.urls import path
from . import views

app_name = 'goods'

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.goods_list, name='list'),
    path('detail/<int:pk>/', views.goods_detail, name='detail'),
    path('search/', views.goods_search, name='search'),
    path('category/<int:pk>/', views.category_list, name='category'),
    path('bargain/', views.bargain_list, name='bargain'),
]
