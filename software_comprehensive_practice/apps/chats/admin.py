from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('order', 'sender', 'receiver', 'chat_type', 'message', 'created_at', 'is_read')
    list_filter = ('chat_type', 'is_read')
    search_fields = ('message',)
