from django.db import models
from django.contrib.auth.models import User


class Rider(models.Model):
    """骑手信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rider')
    real_name = models.CharField('真实姓名', max_length=50)
    phone = models.CharField('手机号', max_length=11)
    id_number = models.CharField('身份证号', max_length=18)
    is_available = models.BooleanField('是否空闲', default=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '骑手'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.real_name} ({self.phone})'

    @property
    def active_deliveries_count(self):
        """当前配送中订单数"""
        return self.deliveries.filter(delivery_status__in=[1, 2]).count()
