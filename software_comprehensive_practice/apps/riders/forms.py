from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Rider


class RiderRegisterForm(forms.Form):
    """骑手注册表单"""
    phone = forms.CharField(
        label='手机号', max_length=11,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入手机号'})
    )
    real_name = forms.CharField(
        label='真实姓名', max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入真实姓名'})
    )
    password = forms.CharField(
        label='密码', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )
    password2 = forms.CharField(
        label='确认密码', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入密码'})
    )
    id_number = forms.CharField(
        label='身份证号', max_length=18,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入身份证号'})
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(username=phone).exists():
            raise forms.ValidationError('该手机号已注册')
        if len(phone) != 11 or not phone.isdigit():
            raise forms.ValidationError('请输入正确的11位手机号')
        return phone

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if Rider.objects.filter(id_number=id_number).exists():
            raise forms.ValidationError('该身份证号已注册')
        if len(id_number) != 18:
            raise forms.ValidationError('请输入正确的18位身份证号')
        return id_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError('两次输入的密码不一致')
        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['phone'],
            password=self.cleaned_data['password'],
        )
        rider = Rider.objects.create(
            user=user,
            real_name=self.cleaned_data['real_name'],
            phone=self.cleaned_data['phone'],
            id_number=self.cleaned_data['id_number'],
        )
        return user


class RiderProfileForm(forms.ModelForm):
    """骑手个人资料表单"""
    class Meta:
        model = Rider
        fields = ['real_name', 'phone', 'id_number']
        widgets = {
            'real_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
