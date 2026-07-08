"""
URL configuration for shop project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# API imports
from apps.users.api_views import LoginAPI, RegisterAPI, LogoutAPI, ProfileAPI, AddressListAPI, AddressDetailAPI
from apps.goods.api_views import CategoryListAPI, CategoryDetailAPI, GoodsListAPI, GoodsDetailAPI
from apps.cart.api_views import CartDetailAPI, CartAddAPI, CartItemUpdateAPI, CartClearAPI
from apps.orders.api_views import OrderListAPI, OrderDetailAPI, CreateOrderAPI, CancelOrderAPI, ConfirmOrderAPI
from apps.payments.api_views import PaymentAPI, PaymentSuccessAPI, PaymentCancelAPI
from apps.reviews.api_views import ReviewListAPI, CreateReviewAPI, DeleteReviewAPI
from apps.merchants.api_views import (
    MerchantRegisterAPI, MerchantDashboardAPI, MerchantGoodsListAPI,
    MerchantGoodsCreateAPI, MerchantGoodsDetailAPI, MerchantOrderListAPI,
    MerchantOrderDetailAPI, MerchantOrderShipAPI
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Token URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Web URLs
    path('', include('apps.goods.urls', namespace='goods')),
    path('users/', include('apps.users.urls', namespace='users')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),
    path('merchant/', include('apps.merchants.urls', namespace='merchants')),
    path('rider/', include('apps.riders.urls', namespace='riders')),
    path('admin-panel/', include('apps.management.urls', namespace='management')),
    path('favorites/', include('apps.favorites.urls', namespace='favorites')),
    path('login/', lambda request: redirect('users:unified_login'), name='login_redirect'),
    
    # API URLs - Users
    path('api/users/login/', LoginAPI.as_view(), name='api_login'),
    path('api/users/register/', RegisterAPI.as_view(), name='api_register'),
    path('api/users/logout/', LogoutAPI.as_view(), name='api_logout'),
    path('api/users/profile/', ProfileAPI.as_view(), name='api_profile'),
    path('api/users/address/', AddressListAPI.as_view(), name='api_address_list'),
    path('api/users/address/<int:pk>/', AddressDetailAPI.as_view(), name='api_address_detail'),
    
    # API URLs - Goods
    path('api/goods/', GoodsListAPI.as_view(), name='api_goods_list'),
    path('api/goods/<int:pk>/', GoodsDetailAPI.as_view(), name='api_goods_detail'),
    path('api/categories/', CategoryListAPI.as_view(), name='api_category_list'),
    path('api/categories/<int:pk>/', CategoryDetailAPI.as_view(), name='api_category_detail'),
    
    # API URLs - Cart
    path('api/cart/', CartDetailAPI.as_view(), name='api_cart_detail'),
    path('api/cart/add/', CartAddAPI.as_view(), name='api_cart_add'),
    path('api/cart/<int:item_id>/', CartItemUpdateAPI.as_view(), name='api_cart_item'),
    path('api/cart/clear/', CartClearAPI.as_view(), name='api_cart_clear'),
    
    # API URLs - Orders
    path('api/orders/', OrderListAPI.as_view(), name='api_order_list'),
    path('api/orders/<int:pk>/', OrderDetailAPI.as_view(), name='api_order_detail'),
    path('api/orders/create/', CreateOrderAPI.as_view(), name='api_order_create'),
    path('api/orders/<int:pk>/cancel/', CancelOrderAPI.as_view(), name='api_order_cancel'),
    path('api/orders/<int:pk>/confirm/', ConfirmOrderAPI.as_view(), name='api_order_confirm'),
    
    # API URLs - Payments
    path('api/payments/<int:order_id>/', PaymentAPI.as_view(), name='api_payment'),
    path('api/payments/<int:order_id>/success/', PaymentSuccessAPI.as_view(), name='api_payment_success'),
    path('api/payments/<int:order_id>/cancel/', PaymentCancelAPI.as_view(), name='api_payment_cancel'),
    
    # API URLs - Reviews
    path('api/reviews/<int:goods_id>/', ReviewListAPI.as_view(), name='api_review_list'),
    path('api/reviews/create/', CreateReviewAPI.as_view(), name='api_review_create'),
    path('api/reviews/<int:pk>/delete/', DeleteReviewAPI.as_view(), name='api_review_delete'),
    
    # API URLs - Merchants
    path('api/merchants/register/', MerchantRegisterAPI.as_view(), name='api_merchant_register'),
    path('api/merchants/dashboard/', MerchantDashboardAPI.as_view(), name='api_merchant_dashboard'),
    path('api/merchants/goods/', MerchantGoodsListAPI.as_view(), name='api_merchant_goods_list'),
    path('api/merchants/goods/create/', MerchantGoodsCreateAPI.as_view(), name='api_merchant_goods_create'),
    path('api/merchants/goods/<int:pk>/', MerchantGoodsDetailAPI.as_view(), name='api_merchant_goods_detail'),
    path('api/merchants/orders/', MerchantOrderListAPI.as_view(), name='api_merchant_order_list'),
    path('api/merchants/orders/<int:pk>/', MerchantOrderDetailAPI.as_view(), name='api_merchant_order_detail'),
    path('api/merchants/orders/<int:pk>/ship/', MerchantOrderShipAPI.as_view(), name='api_merchant_order_ship'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
