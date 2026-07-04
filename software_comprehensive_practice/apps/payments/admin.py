from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_no', 'order', 'amount', 'method', 'status', 'paid_at']
    list_filter = ['status', 'method']
    search_fields = ['payment_no', 'order__order_no']
    readonly_fields = ['payment_no', 'created_at']
