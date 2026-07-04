from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Merchant(models.Model):
    """商家信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant')
    shop_name = models.CharField('店铺名称', max_length=100)
    shop_logo = models.ImageField('店铺Logo', upload_to='merchants/logos/', blank=True, null=True)
    shop_description = models.TextField('店铺简介', blank=True)
    contact_phone = models.CharField('联系电话', max_length=11)
    contact_email = models.EmailField('联系邮箱', blank=True)
    address = models.CharField('店铺地址', max_length=200)
    is_verified = models.BooleanField('是否已认证', default=False)
    is_active = models.BooleanField('是否营业', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '商家'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.shop_name

    @property
    def total_goods(self):
        """商品总数"""
        return self.goods.count()

    @property
    def total_sales(self):
        """总销量"""
        return sum(goods.sales for goods in self.goods.all())

    @property
    def total_revenue(self):
        """预估总收入"""
        from apps.orders.models import OrderItem
        items = OrderItem.objects.filter(
            goods__merchant_goods__merchant=self,
            order__status__in=[2, 3, 4]
        )
        return sum(item.subtotal for item in items)


class MerchantGoods(models.Model):
    """商家商品（扩展Goods模型，关联商家）"""
    goods = models.OneToOneField('goods.Goods', on_delete=models.CASCADE, related_name='merchant_goods')
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='goods')
    cost_price = models.DecimalField('成本价', max_digits=10, decimal_places=2, default=0)
    is_featured = models.BooleanField('是否推荐', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '商家商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.merchant.shop_name} - {self.goods.name}'

    @property
    def profit(self):
        """预估利润"""
        return (self.goods.price - self.cost_price) * self.goods.sales
