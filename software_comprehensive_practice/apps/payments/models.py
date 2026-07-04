from django.db import models
from apps.orders.models import Order
import uuid


class Payment(models.Model):
    """支付记录"""
    METHOD_CHOICES = [
        (1, '支付宝'),
        (2, '微信支付'),
        (3, '银行卡'),
    ]

    STATUS_CHOICES = [
        (1, '待支付'),
        (2, '支付成功'),
        (3, '支付失败'),
        (4, '已退款'),
    ]

    payment_no = models.CharField('支付单号', max_length=32, unique=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField('支付金额', max_digits=10, decimal_places=2)
    method = models.IntegerField('支付方式', choices=METHOD_CHOICES, default=1)
    status = models.IntegerField('支付状态', choices=STATUS_CHOICES, default=1)
    paid_at = models.DateTimeField('支付时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '支付记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.payment_no

    def save(self, *args, **kwargs):
        if not self.payment_no:
            self.payment_no = uuid.uuid4().hex.upper()[:32]
        super().save(*args, **kwargs)

    @property
    def status_text(self):
        return dict(self.STATUS_CHOICES).get(self.status, '未知')

    @property
    def method_text(self):
        return dict(self.METHOD_CHOICES).get(self.method, '未知')
