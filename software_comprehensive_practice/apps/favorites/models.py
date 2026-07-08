from django.db import models
from django.contrib.auth.models import User
from apps.goods.models import Goods


class Favorite(models.Model):
    """商品收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='用户')
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='favorites', verbose_name='商品')
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        verbose_name = '商品收藏'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'goods')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} 收藏 {self.goods.name}'
