from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Merchant, MerchantGoods
from apps.goods.models import Goods, Category


class MerchantRegisterForm(UserCreationForm):
    """商家注册表单"""
    email = forms.EmailField(label='邮箱', required=True)
    shop_name = forms.CharField(label='店铺名称', max_length=100)
    contact_phone = forms.CharField(label='联系电话', max_length=11)
    address = forms.CharField(label='店铺地址', max_length=200)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        return email


class MerchantProfileForm(forms.ModelForm):
    """商家信息表单"""
    class Meta:
        model = Merchant
        fields = ['shop_name', 'shop_logo', 'shop_description', 'contact_phone', 'contact_email', 'address']
        widgets = {
            'shop_description': forms.Textarea(attrs={'rows': 4}),
        }


class GoodsForm(forms.ModelForm):
    """商品表单"""
    class Meta:
        model = Goods
        fields = ['name', 'description', 'price', 'stock', 'category', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class MerchantGoodsForm(forms.ModelForm):
    """商家商品扩展表单"""
    class Meta:
        model = MerchantGoods
        fields = ['cost_price', 'is_featured']
