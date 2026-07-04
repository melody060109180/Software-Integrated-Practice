from django.db import models
from django.contrib.auth.models import User
from apps.goods.models import Goods
from apps.orders.models import Order


class Review(models.Model):
    """商品评价"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField('评分', choices=[(i, i) for i in range(1, 6)])
    content = models.TextField('评价内容', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '商品评价'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        unique_together = ('user', 'goods')

    def __str__(self):
        return f'{self.user.username}评价{self.goods.name}'

    @property
    def rating_stars(self):
        return '★' * self.rating + '☆' * (5 - self.rating)
