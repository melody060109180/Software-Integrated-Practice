from django.contrib import admin
from .models import Merchant, MerchantGoods


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ['shop_name', 'user', 'contact_phone', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'is_active']
    search_fields = ['shop_name', 'user__username', 'contact_phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MerchantGoods)
class MerchantGoodsAdmin(admin.ModelAdmin):
    list_display = ['merchant', 'goods', 'cost_price', 'is_featured', 'created_at']
    list_filter = ['is_featured']
    search_fields = ['merchant__shop_name', 'goods__name']
    readonly_fields = ['created_at']
