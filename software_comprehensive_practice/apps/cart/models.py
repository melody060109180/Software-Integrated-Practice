from django.db import models
from django.contrib.auth.models import User
from apps.goods.models import Goods


class Cart(models.Model):
    """购物车"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username}的购物车'

    @property
    def total_price(self):
        """计算购物车总价（使用动态价格）"""
        from decimal import Decimal
        total = Decimal('0')
        for item in self.items.all():
            total += item.subtotal
        return total

    @property
    def total_quantity(self):
        """计算购物车总数量"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """购物车商品"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name='商品')
    quantity = models.PositiveIntegerField('数量', default=1)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '购物车商品'
        verbose_name_plural = verbose_name
        unique_together = ('cart', 'goods')

    def __str__(self):
        return f'{self.goods.name} x {self.quantity}'

    @property
    def subtotal(self):
        """计算小计（使用动态价格）"""
        from decimal import Decimal
        current_price = Decimal(str(self.goods.current_price))
        return current_price * self.quantity
