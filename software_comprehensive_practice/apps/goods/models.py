from django.db import models
from django.urls import reverse


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
