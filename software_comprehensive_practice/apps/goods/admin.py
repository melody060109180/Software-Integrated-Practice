from django.contrib import admin
from .models import Category, Goods


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'sort_order', 'created_at']
    list_filter = ['parent']
    search_fields = ['name']


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'sales', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'is_active']
