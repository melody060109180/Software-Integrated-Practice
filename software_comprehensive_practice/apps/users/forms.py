from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile, Address


class UserRegisterForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(label='邮箱', required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        return email


class UserLoginForm(AuthenticationForm):
    """用户登录表单"""
    username = forms.CharField(label='用户名', max_length=150)
    password = forms.CharField(label='密码', widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    """个人信息表单"""
    class Meta:
        model = Profile
        fields = ['avatar', 'phone', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AddressForm(forms.ModelForm):
    """收货地址表单"""
    class Meta:
        model = Address
        fields = ['name', 'phone', 'province', 'city', 'district', 'detail', 'is_default']
        widgets = {
            'detail': forms.Textarea(attrs={'rows': 3}),
        }
