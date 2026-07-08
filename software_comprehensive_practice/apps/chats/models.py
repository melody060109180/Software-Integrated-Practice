from django.db import models
from django.contrib.auth.models import User
from apps.orders.models import Order


class ChatMessage(models.Model):
    """配送过程中的临时对话消息"""
    CHAT_TYPE_CHOICES = (
        ('user_merchant', '用户-商家'),
        ('user_rider', '用户-骑手'),
        ('rider_merchant', '骑手-商家'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='chat_messages', verbose_name='关联订单')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_chat_messages', verbose_name='发送者')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_chat_messages', verbose_name='接收者')
    chat_type = models.CharField('对话类型', max_length=20, choices=CHAT_TYPE_CHOICES)
    message = models.TextField('消息内容')
    created_at = models.DateTimeField('发送时间', auto_now_add=True)
    is_read = models.BooleanField('已读', default=False)

    class Meta:
        verbose_name = '聊天消息'
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    def __str__(self):
        return f'Order {self.order.order_no}: {self.sender} -> {self.receiver}: {self.message[:30]}'
