from django.contrib import admin
from .models import Rider


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ['real_name', 'phone', 'id_number', 'is_available', 'is_active', 'created_at']
    list_filter = ['is_available', 'is_active']
    search_fields = ['real_name', 'phone', 'id_number']
