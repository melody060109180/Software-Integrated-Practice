from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import Merchant, MerchantGoods
from .forms import MerchantRegisterForm, MerchantProfileForm, GoodsForm, MerchantGoodsForm
from apps.goods.models import Goods, Category
from apps.orders.models import Order, OrderItem


def merchant_register(request):
    """商家注册"""
    if request.method == 'POST':
        form = MerchantRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 创建商家信息
            Merchant.objects.create(
                user=user,
                shop_name=form.cleaned_data['shop_name'],
                contact_phone=form.cleaned_data['contact_phone'],
                address=form.cleaned_data['address'],
            )
            # 自动登录
            login(request, user)
            messages.success(request, '商家注册成功！')
            return redirect('merchants:dashboard')
    else:
        form = MerchantRegisterForm()
    return render(request, 'merchants/register.html', {'form': form})


def merchant_login(request):
    """商家登录"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and hasattr(user, 'merchant'):
            login(request, user)
            messages.success(request, '登录成功！')
            return redirect('merchants:dashboard')
        else:
            messages.error(request, '用户名或密码错误，或该账号不是商家账号')
    return render(request, 'merchants/login.html')


@login_required
def merchant_logout(request):
    """商家登出"""
    if request.method != 'POST':
        return redirect('merchants:dashboard')
    logout(request)
    messages.success(request, '已退出登录')
    return redirect('merchants:login')


@login_required
def dashboard(request):
    """商家后台首页 - 数据统计"""
    merchant = get_object_or_404(Merchant, user=request.user)
    
    # 时间统计
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # 商品统计
    total_goods = merchant.goods.count()
    active_goods = merchant.goods.filter(goods__is_active=True).count()
    
    # 订单统计
    merchant_goods_ids = merchant.goods.values_list('goods_id', flat=True)
    total_orders = Order.objects.filter(items__goods_id__in=merchant_goods_ids).distinct().count()
    month_orders = Order.objects.filter(
        items__goods_id__in=merchant_goods_ids,
        created_at__date__gte=month_start
    ).distinct().count()
    
    # 销售统计
    total_sales = OrderItem.objects.filter(
        goods_id__in=merchant_goods_ids,
        order__status__in=[2, 3, 4]
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    month_sales = OrderItem.objects.filter(
        goods_id__in=merchant_goods_ids,
        order__status__in=[2, 3, 4],
        order__created_at__date__gte=month_start
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # 收入统计
    total_revenue = OrderItem.objects.filter(
        goods_id__in=merchant_goods_ids,
        order__status__in=[2, 3, 4]
    ).aggregate(total=Sum(F('goods_price') * F('quantity')))['total'] or 0
    
    month_revenue = OrderItem.objects.filter(
        goods_id__in=merchant_goods_ids,
        order__status__in=[2, 3, 4],
        order__created_at__date__gte=month_start
    ).aggregate(total=Sum(F('goods_price') * F('quantity')))['total'] or 0
    
    # 最近订单
    recent_orders = Order.objects.filter(
        items__goods_id__in=merchant_goods_ids
    ).distinct().order_by('-created_at')[:5]
    
    context = {
        'merchant': merchant,
        'total_goods': total_goods,
        'active_goods': active_goods,
        'total_orders': total_orders,
        'month_orders': month_orders,
        'total_sales': total_sales,
        'month_sales': month_sales,
        'total_revenue': total_revenue,
        'month_revenue': month_revenue,
        'recent_orders': recent_orders,
    }
    return render(request, 'merchants/dashboard.html', context)


@login_required
def profile(request):
    """商家信息"""
    merchant = get_object_or_404(Merchant, user=request.user)
    return render(request, 'merchants/profile.html', {'merchant': merchant})


@login_required
def profile_edit(request):
    """编辑商家信息"""
    merchant = get_object_or_404(Merchant, user=request.user)
    if request.method == 'POST':
        form = MerchantProfileForm(request.POST, request.FILES, instance=merchant)
        if form.is_valid():
            form.save()
            messages.success(request, '店铺信息更新成功！')
            return redirect('merchants:profile')
    else:
        form = MerchantProfileForm(instance=merchant)
    return render(request, 'merchants/profile_edit.html', {'form': form, 'merchant': merchant})


@login_required
def goods_list(request):
    """商品列表"""
    merchant = get_object_or_404(Merchant, user=request.user)
    keyword = request.GET.get('keyword', '')
    status = request.GET.get('status', '')
    
    merchant_goods = MerchantGoods.objects.filter(merchant=merchant).select_related('goods', 'goods__category')
    
    if keyword:
        merchant_goods = merchant_goods.filter(
            Q(goods__name__icontains=keyword) | Q(goods__description__icontains=keyword)
        )
    
    if status == 'active':
        merchant_goods = merchant_goods.filter(goods__is_active=True)
    elif status == 'inactive':
        merchant_goods = merchant_goods.filter(goods__is_active=False)
    
    return render(request, 'merchants/goods_list.html', {
        'merchant_goods': merchant_goods,
        'keyword': keyword,
        'status': status,
    })


@login_required
def goods_add(request):
    """添加商品"""
    merchant = get_object_or_404(Merchant, user=request.user)
    
    if request.method == 'POST':
        goods_form = GoodsForm(request.POST, request.FILES)
        merchant_goods_form = MerchantGoodsForm(request.POST)
        
        if goods_form.is_valid() and merchant_goods_form.is_valid():
            goods = goods_form.save()
            merchant_goods = merchant_goods_form.save(commit=False)
            merchant_goods.goods = goods
            merchant_goods.merchant = merchant
            merchant_goods.save()
            
            messages.success(request, '商品添加成功！')
            return redirect('merchants:goods_list')
    else:
        goods_form = GoodsForm()
        merchant_goods_form = MerchantGoodsForm()
    
    return render(request, 'merchants/goods_form.html', {
        'goods_form': goods_form,
        'merchant_goods_form': merchant_goods_form,
        'title': '添加商品',
    })


@login_required
def goods_edit(request, pk):
    """编辑商品"""
    merchant = get_object_or_404(Merchant, user=request.user)
    merchant_goods = get_object_or_404(MerchantGoods, pk=pk, merchant=merchant)
    goods = merchant_goods.goods
    
    if request.method == 'POST':
        goods_form = GoodsForm(request.POST, request.FILES, instance=goods)
        merchant_goods_form = MerchantGoodsForm(request.POST, instance=merchant_goods)
        
        if goods_form.is_valid() and merchant_goods_form.is_valid():
            goods_form.save()
            merchant_goods_form.save()
            
            messages.success(request, '商品更新成功！')
            return redirect('merchants:goods_list')
    else:
        goods_form = GoodsForm(instance=goods)
        merchant_goods_form = MerchantGoodsForm(instance=merchant_goods)
    
    return render(request, 'merchants/goods_form.html', {
        'goods_form': goods_form,
        'merchant_goods_form': merchant_goods_form,
        'title': '编辑商品',
        'merchant_goods': merchant_goods,
    })


@login_required
def goods_delete(request, pk):
    """删除商品"""
    merchant = get_object_or_404(Merchant, user=request.user)
    merchant_goods = get_object_or_404(MerchantGoods, pk=pk, merchant=merchant)
    
    if request.method == 'POST':
        goods = merchant_goods.goods
        merchant_goods.delete()
        goods.delete()
        messages.success(request, '商品已删除！')
    
    return redirect('merchants:goods_list')


@login_required
def goods_toggle(request, pk):
    """上下架商品"""
    if request.method != 'POST':
        return redirect('merchants:goods_list')
    merchant = get_object_or_404(Merchant, user=request.user)
    merchant_goods = get_object_or_404(MerchantGoods, pk=pk, merchant=merchant)
    
    goods = merchant_goods.goods
    goods.is_active = not goods.is_active
    goods.save()
    
    status = '上架' if goods.is_active else '下架'
    messages.success(request, f'商品已{status}！')
    
    return redirect('merchants:goods_list')


@login_required
def order_list(request):
    """订单列表"""
    merchant = get_object_or_404(Merchant, user=request.user)
    merchant_goods_ids = merchant.goods.values_list('goods_id', flat=True)
    
    status = request.GET.get('status', '')
    
    orders = Order.objects.filter(
        items__goods_id__in=merchant_goods_ids
    ).distinct().order_by('-created_at')
    
    if status:
        orders = orders.filter(status=status)
    
    # 为每个订单计算该商家的商品小计
    for order in orders:
        order.merchant_items = order.items.filter(goods_id__in=merchant_goods_ids)
        order.merchant_subtotal = sum(item.subtotal for item in order.merchant_items)
    
    return render(request, 'merchants/order_list.html', {
        'orders': orders,
        'status': status,
    })


@login_required
def order_detail(request, pk):
    """订单详情"""
    merchant = get_object_or_404(Merchant, user=request.user)
    merchant_goods_ids = merchant.goods.values_list('goods_id', flat=True)
    
    order = get_object_or_404(Order, pk=pk)
    merchant_items = order.items.filter(goods_id__in=merchant_goods_ids)
    merchant_subtotal = sum(item.subtotal for item in merchant_items)
    
    return render(request, 'merchants/order_detail.html', {
        'order': order,
        'merchant_items': merchant_items,
        'merchant_subtotal': merchant_subtotal,
    })


@login_required
def order_ship(request, pk):
    """发货"""
    if request.method != 'POST':
        return redirect('merchants:order_detail', pk=pk)
    merchant = get_object_or_404(Merchant, user=request.user)
    merchant_goods_ids = merchant.goods.values_list('goods_id', flat=True)
    order = get_object_or_404(Order, pk=pk, items__goods_id__in=merchant_goods_ids)
    
    if order.status == 2:  # 已支付
        order.status = 3  # 已发货
        order.shipped_at = timezone.now()
        order.save()
        messages.success(request, '订单已发货！')
    else:
        messages.error(request, '该订单无法发货')
    
    return redirect('merchants:order_detail', pk=pk)
