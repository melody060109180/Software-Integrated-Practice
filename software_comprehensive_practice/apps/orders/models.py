from django.db import models
from django.contrib.auth.models import User
from apps.goods.models import Goods
import uuid


class Order(models.Model):
    """订单"""
    STATUS_CHOICES = [
        (1, '待支付'),
        (2, '已支付'),
        (3, '已发货'),
        (4, '已完成'),
        (5, '已取消'),
    ]

    DELIVERY_STATUS_CHOICES = [
        (0, '未分配'),
        (1, '待配送'),
        (2, '配送中'),
        (3, '已送达'),
    ]

    order_no = models.CharField('订单号', max_length=32, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField('订单总额', max_digits=10, decimal_places=2)
    status = models.IntegerField('订单状态', choices=STATUS_CHOICES, default=1)
    receiver_name = models.CharField('收货人', max_length=50)
    receiver_phone = models.CharField('收货电话', max_length=11)
    receiver_address = models.CharField('收货地址', max_length=300)
    remark = models.TextField('订单备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    paid_at = models.DateTimeField('支付时间', blank=True, null=True)
    shipped_at = models.DateTimeField('发货时间', blank=True, null=True)
    completed_at = models.DateTimeField('完成时间', blank=True, null=True)

    # 配送相关字段
    rider = models.ForeignKey(
        'riders.Rider', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='deliveries',
        verbose_name='配送骑手'
    )
    delivery_status = models.IntegerField(
        '配送状态', choices=DELIVERY_STATUS_CHOICES, default=0
    )
    assigned_at = models.DateTimeField('指派时间', blank=True, null=True)
    delivered_at = models.DateTimeField('送达时间', blank=True, null=True)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = uuid.uuid4().hex.upper()[:32]
        super().save(*args, **kwargs)

    @property
    def status_text(self):
        return dict(self.STATUS_CHOICES).get(self.status, '未知')

    def can_cancel(self):
        return self.status == 1

    def can_confirm(self):
        return self.status in [3, 4]


class OrderItem(models.Model):
    """订单商品"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    goods = models.ForeignKey(Goods, on_delete=models.SET_NULL, null=True)
    goods_name = models.CharField('商品名称', max_length=200)
    goods_price = models.DecimalField('商品价格', max_digits=10, decimal_places=2)
    goods_image = models.CharField('商品图片', max_length=500, blank=True, null=True)
    quantity = models.PositiveIntegerField('数量', default=1)

    class Meta:
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.goods_name} x {self.quantity}'

    @property
    def subtotal(self):
        return self.goods_price * self.quantity
