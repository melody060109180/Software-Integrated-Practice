from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'goods', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['user__username', 'goods__name', 'content']
    readonly_fields = ['created_at']
