from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    path('<int:order_id>/', views.chat_page, name='chat'),
    path('<int:order_id>/messages/<int:user_id>/', views.chat_messages, name='chat_messages'),
    path('send/', views.chat_send, name='chat_send'),
]
