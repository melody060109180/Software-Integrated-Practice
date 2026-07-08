from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import UserRegisterForm, UserLoginForm, ProfileForm, AddressForm
from .models import Profile, Address
from apps.cart.models import Cart
from apps.merchants.models import Merchant


def register(request):
    """用户注册"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Cart.objects.get_or_create(user=user)
            messages.success(request, '注册成功！')
            return redirect('goods:list')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """用户登录"""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # 合并Session购物车
            _merge_session_cart(request, user)
            messages.success(request, '登录成功！')
            return redirect(request.GET.get('next', 'goods:list'))
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


def unified_login(request):
    """统一登录页面 - 区分用户、管理员、骑手"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        login_type = request.POST.get('login_type', 'user')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if login_type == 'user':
                # 普通用户
                if user.is_staff:
                    messages.error(request, '该账号是管理员账号，请选择管理员登录！')
                elif hasattr(user, 'rider'):
                    messages.error(request, '该账号是骑手账号，请选择"骑手"登录！')
                else:
                    login(request, user)
                    _merge_session_cart(request, user)
                    messages.success(request, '用户登录成功！')
                    return redirect(request.GET.get('next', 'goods:list'))

            elif login_type == 'admin':
                # 管理员：必须是staff
                if user.is_staff:
                    login(request, user)
                    messages.success(request, '管理员登录成功！')
                    return redirect('merchants:dashboard')
                elif hasattr(user, 'rider'):
                    messages.error(request, '该账号是骑手账号，请选择"骑手"登录！')
                else:
                    messages.error(request, '该账号没有管理员权限！')

            elif login_type == 'rider':
                # 骑手：必须有rider属性
                if hasattr(user, 'rider'):
                    login(request, user)
                    messages.success(request, '骑手登录成功！')
                    return redirect('riders:dashboard')
                elif user.is_staff:
                    messages.error(request, '该账号是管理员账号，请选择"管理员"登录！')
                else:
                    messages.error(request, '该账号不是骑手账号，请先注册骑手！')
        else:
            messages.error(request, '用户名/手机号或密码错误！')

    return render(request, 'users/unified_login.html')


def _merge_session_cart(request, user):
    """合并Session购物车到用户购物车"""
    session_cart = request.session.get('cart', {})
    if session_cart:
        user_cart, _ = Cart.objects.get_or_create(user=user)
        for goods_id, quantity in session_cart.items():
            from apps.goods.models import Goods
            goods = Goods.objects.filter(id=goods_id).first()
            if goods:
                from apps.cart.models import CartItem
                cart_item, created = CartItem.objects.get_or_create(
                    cart=user_cart, goods=goods,
                    defaults={'quantity': quantity}
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
        request.session['cart'] = {}


@login_required
def logout_view(request):
    """用户登出"""
    if request.method != 'POST':
        return redirect('users:profile')
    logout(request)
    messages.success(request, '已成功退出登录！')
    return redirect('goods:list')


@login_required
def profile(request):
    """个人中心"""
    return render(request, 'users/profile.html')


@login_required
def profile_edit(request):
    """修改个人信息"""
    profile_obj = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息修改成功！')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=profile_obj)
    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def password_change(request):
    """修改密码"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not request.user.check_password(old_password):
            messages.error(request, '原密码错误！')
        elif new_password1 != new_password2:
            messages.error(request, '两次输入的新密码不一致！')
        elif len(new_password1) < 8:
            messages.error(request, '新密码长度不能少于8位！')
        else:
            request.user.set_password(new_password1)
            request.user.save()
            messages.success(request, '密码修改成功，请重新登录！')
            return redirect('users:login')
    return render(request, 'users/password_change.html')


@login_required
def address_list(request):
    """收货地址列表"""
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'users/address_list.html', {'addresses': addresses})


@login_required
def address_add(request):
    """添加收货地址"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, '收货地址添加成功！')
            return redirect('users:address_list')
    else:
        form = AddressForm()
    return render(request, 'users/address_form.html', {'form': form, 'title': '添加收货地址'})


@login_required
def address_edit(request, pk):
    """编辑收货地址"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, '收货地址修改成功！')
            return redirect('users:address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'users/address_form.html', {'form': form, 'title': '编辑收货地址'})


@login_required
def address_delete(request, pk):
    """删除收货地址"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, '收货地址删除成功！')
    return redirect('users:address_list')
