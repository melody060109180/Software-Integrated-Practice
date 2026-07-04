from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('<int:order_id>/', views.pay, name='pay'),
    path('success/<int:order_id>/', views.payment_success, name='success'),
    path('cancel/<int:order_id>/', views.payment_cancel, name='cancel'),
]
