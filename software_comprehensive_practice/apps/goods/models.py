from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import date


class Category(models.Model):
    """商品分类"""
    name = models.CharField('分类名称', max_length=50)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='children', verbose_name='父分类')
    icon = models.CharField('图标', max_length=50, blank=True, null=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Goods(models.Model):
    """商品"""
    name = models.CharField('商品名称', max_length=200)
    description = models.TextField('商品描述', blank=True)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField('库存', default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,
                                  related_name='goods', verbose_name='商品分类')
    image = models.ImageField('商品图片', upload_to='goods/', blank=True, null=True)
    is_active = models.BooleanField('是否上架', default=True)
    sales = models.PositiveIntegerField('销量', default=0)
    
    # 保质期相关字段
    production_date = models.DateField('生产日期', null=True, blank=True)
    shelf_life_days = models.PositiveIntegerField('保质期(天)', default=365)
    
    # 重量体积字段（防爆单用）
    weight = models.DecimalField('重量(kg)', max_digits=6, decimal_places=2, default=0.5)
    length = models.DecimalField('长(cm)', max_digits=6, decimal_places=1, default=20)
    width = models.DecimalField('宽(cm)', max_digits=6, decimal_places=1, default=15)
    height = models.DecimalField('高(cm)', max_digits=6, decimal_places=1, default=10)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('goods:detail', kwargs={'pk': self.pk})

    @property
    def average_rating(self):
        """获取平均评分"""
        from apps.reviews.models import Review
        reviews = Review.objects.filter(goods=self)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0

    @property
    def review_count(self):
        """获取评价数量"""
        from apps.reviews.models import Review
        return Review.objects.filter(goods=self).count()
    
    @property
    def expiry_date(self):
        """计算保质期截止日期"""
        if self.production_date and self.shelf_life_days:
            from datetime import timedelta
            return self.production_date + timedelta(days=self.shelf_life_days)
        return None
    
    @property
    def days_until_expiry(self):
        """计算距离过期还有多少天"""
        if self.expiry_date:
            delta = self.expiry_date - date.today()
            return delta.days
        return None
    
    @property
    def is_expired(self):
        """是否已过期"""
        days = self.days_until_expiry
        return days is not None and days < 0
    
    @property
    def is_near_expiry(self):
        """是否临期（14天内）"""
        days = self.days_until_expiry
        return days is not None and 0 <= days <= 14
    
    @property
    def discount_rate(self):
        """计算折扣率"""
        days = self.days_until_expiry
        if days is None:
            return 1.0
        if days < 0:  # 已过期
            return 0
        if days <= 3:  # 3天内：3折
            return 0.3
        if days <= 7:  # 7天内：5折
            return 0.5
        if days <= 14:  # 14天内：7折
            return 0.7
        return 1.0
    
    @property
    def current_price(self):
        """当前动态价格"""
        return round(float(self.price) * self.discount_rate, 2)
    
    @property
    def discount_text(self):
        """折扣文案"""
        days = self.days_until_expiry
        if days is None:
            return None
        if days < 0:
            return '已过期'
        if days <= 3:
            return '限时3折'
        if days <= 7:
            return '限时5折'
        if days <= 14:
            return '限时7折'
        return None
    
    @property
    def volume(self):
        """计算体积(m³)"""
        return float(self.length * self.width * self.height) / 1000000
    
    @property
    def weight_text(self):
        """重量文案"""
        if self.weight < 1:
            return f"{self.weight * 1000:.0f}g"
        return f"{self.weight:.1f}kg"
