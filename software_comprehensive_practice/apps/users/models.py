from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """用户个人信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    phone = models.CharField('手机号', max_length=11, blank=True, null=True)
    birth_date = models.DateField('出生日期', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username}的个人信息'


class Address(models.Model):
    """收货地址"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField('收货人', max_length=50)
    phone = models.CharField('联系电话', max_length=11)
    province = models.CharField('省份', max_length=50)
    city = models.CharField('城市', max_length=50)
    district = models.CharField('区/县', max_length=50)
    detail = models.CharField('详细地址', max_length=200)
    is_default = models.BooleanField('默认地址', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f'{self.name} - {self.province}{self.city}{self.district}{self.detail}'

    def full_address(self):
        return f'{self.province}{self.city}{self.district}{self.detail}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """创建用户时自动创建个人信息"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """保存用户时自动保存个人信息"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)
