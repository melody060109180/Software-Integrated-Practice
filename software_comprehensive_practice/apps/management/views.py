from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from apps.merchants.models import Merchant, MerchantGoods
from apps.goods.models import Goods, Category
from apps.orders.models import Order, OrderItem
from apps.reviews.models import Review
from apps.riders.models import Rider


def admin_required(view_func):
    """管理员权限装饰器"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:unified_login')
        if not request.user.is_staff:
            messages.error(request, '无权访问！')
            return redirect('goods:index')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def dashboard(request):
    """数据统计仪表盘"""
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # 今日统计
    today_orders = Order.objects.filter(created_at__date=today).count()
    today_revenue = Order.objects.filter(
        created_at__date=today, 
        status__in=[2, 3, 4]
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    today_users = User.objects.filter(date_joined__date=today).count()
    
    # 本月统计
    month_orders = Order.objects.filter(created_at__date__gte=month_start).count()
    month_revenue = Order.objects.filter(
        created_at__date__gte=month_start,
        status__in=[2, 3, 4]
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    month_users = User.objects.filter(date_joined__date__gte=month_start).count()
    
    # 总体统计
    total_users = User.objects.filter(is_staff=False).count()
    total_merchants = Merchant.objects.count()
    total_goods = Goods.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(
        status__in=[2, 3, 4]
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_riders = Rider.objects.count()
    available_riders = Rider.objects.filter(is_available=True, is_active=True).count()
    
    # 订单状态分布
    pending_payment = Order.objects.filter(status=1).count()
    pending_ship = Order.objects.filter(status=2).count()
    shipped = Order.objects.filter(status=3).count()
    completed = Order.objects.filter(status=4).count()
    cancelled = Order.objects.filter(status=5).count()
    
    # 热销商品排行
    hot_goods = Goods.objects.order_by('-sales')[:10]
    
    # 最近订单
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # 月度销售趋势（最近6个月）
    six_months_ago = today - timedelta(days=180)
    monthly_sales = Order.objects.filter(
        created_at__date__gte=six_months_ago,
        status__in=[2, 3, 4]
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('month')
    
    context = {
        # 今日
        'today_orders': today_orders,
        'today_revenue': today_revenue,
        'today_users': today_users,
        # 本月
        'month_orders': month_orders,
        'month_revenue': month_revenue,
        'month_users': month_users,
        # 总体
        'total_users': total_users,
        'total_merchants': total_merchants,
        'total_goods': total_goods,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_riders': total_riders,
        'available_riders': available_riders,
        # 订单状态
        'pending_payment': pending_payment,
        'pending_ship': pending_ship,
        'shipped': shipped,
        'completed': completed,
        'cancelled': cancelled,
        # 排行
        'hot_goods': hot_goods,
        'recent_orders': recent_orders,
        'monthly_sales': list(monthly_sales),
    }
    return render(request, 'management/dashboard.html', context)


# ==================== 用户管理 ====================

@admin_required
def user_list(request):
    """用户列表"""
    users = User.objects.filter(is_staff=False).select_related('profile').order_by('-date_joined')
    
    # 搜索
    keyword = request.GET.get('keyword')
    if keyword:
        users = users.filter(
            Q(username__icontains=keyword) |
            Q(email__icontains=keyword) |
            Q(profile__phone__icontains=keyword)
        )
    
    # 状态筛选
    status = request.GET.get('status')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'disabled':
        users = users.filter(is_active=False)
    
    # 分页
    paginator = Paginator(users, 15)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    return render(request, 'management/user_list.html', {'users': users})


@admin_required
def user_detail(request, pk):
    """用户详情"""
    target_user = get_object_or_404(User.objects.select_related('profile'), pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_active':
            target_user.is_active = not target_user.is_active
            target_user.save()
            status = '启用' if target_user.is_active else '禁用'
            messages.success(request, f'用户已{status}')
        elif action == 'delete':
            target_user.delete()
            messages.success(request, '用户已删除')
            return redirect('management:user_list')
    
    # 用户的订单
    user_orders = Order.objects.filter(user=target_user).order_by('-created_at')[:10]
    # 用户的评价
    user_reviews = Review.objects.filter(user=target_user).select_related('goods').order_by('-created_at')[:10]
    
    context = {
        'target_user': target_user,
        'user_orders': user_orders,
        'user_reviews': user_reviews,
    }
    return render(request, 'management/user_detail.html', context)


# ==================== 商家管理 ====================

@admin_required
def merchant_list(request):
    """商家列表"""
    merchants = Merchant.objects.select_related('user').order_by('-created_at')
    
    # 搜索
    keyword = request.GET.get('keyword')
    if keyword:
        merchants = merchants.filter(
            Q(shop_name__icontains=keyword) |
            Q(user__username__icontains=keyword) |
            Q(contact_phone__icontains=keyword)
        )
    
    # 认证状态筛选
    status = request.GET.get('status')
    if status == 'verified':
        merchants = merchants.filter(is_verified=True)
    elif status == 'unverified':
        merchants = merchants.filter(is_verified=False)
    elif status == 'inactive':
        merchants = merchants.filter(is_active=False)
    
    # 分页
    paginator = Paginator(merchants, 15)
    page = request.GET.get('page')
    merchants = paginator.get_page(page)
    
    return render(request, 'management/merchant_list.html', {'merchants': merchants})


@admin_required
def merchant_detail(request, pk):
    """商家详情"""
    merchant = get_object_or_404(Merchant.objects.select_related('user'), pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'verify':
            merchant.is_verified = True
            merchant.save()
            messages.success(request, '商家已认证')
        elif action == 'revoke_verify':
            merchant.is_verified = False
            merchant.save()
            messages.success(request, '已撤销认证')
        elif action == 'toggle_active':
            merchant.is_active = not merchant.is_active
            merchant.save()
            status = '启用' if merchant.is_active else '禁用'
            messages.success(request, f'商家已{status}')
    
    # 商家的商品
    merchant_goods = MerchantGoods.objects.filter(merchant=merchant).select_related('goods')[:20]
    
    context = {
        'merchant': merchant,
        'merchant_goods': merchant_goods,
    }
    return render(request, 'management/merchant_detail.html', context)


# ==================== 商品管理 ====================

@admin_required
def goods_list(request):
    """商品列表"""
    goods = Goods.objects.select_related('category', 'merchant_goods__merchant').order_by('-created_at')
    
    # 搜索
    keyword = request.GET.get('keyword')
    if keyword:
        goods = goods.filter(
            Q(name__icontains=keyword) |
            Q(description__icontains=keyword)
        )
    
    # 状态筛选
    status = request.GET.get('status')
    if status == 'active':
        goods = goods.filter(is_active=True)
    elif status == 'inactive':
        goods = goods.filter(is_active=False)
    
    # 分类筛选
    category_id = request.GET.get('category')
    if category_id:
        goods = goods.filter(category_id=category_id)
    
    # 分页
    paginator = Paginator(goods, 15)
    page = request.GET.get('page')
    goods = paginator.get_page(page)
    
    categories = Category.objects.all()
    
    context = {
        'goods': goods,
        'categories': categories,
    }
    return render(request, 'management/goods_list.html', context)


@admin_required
def goods_detail(request, pk):
    """商品详情"""
    goods = get_object_or_404(
        Goods.objects.select_related('category', 'merchant_goods__merchant'), 
        pk=pk
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_active':
            goods.is_active = not goods.is_active
            goods.save()
            status = '上架' if goods.is_active else '下架'
            messages.success(request, f'商品已{status}')
        elif action == 'delete':
            goods.delete()
            messages.success(request, '商品已删除')
            return redirect('management:goods_list')
    
    # 商品的评价
    goods_reviews = Review.objects.filter(goods=goods).select_related('user').order_by('-created_at')[:20]
    
    context = {
        'goods': goods,
        'goods_reviews': goods_reviews,
    }
    return render(request, 'management/goods_detail.html', context)


# ==================== 订单管理 ====================

@admin_required
def order_list(request):
    """订单列表"""
    orders = Order.objects.select_related('user').order_by('-created_at')
    
    # 搜索
    keyword = request.GET.get('keyword')
    if keyword:
        orders = orders.filter(
            Q(order_no__icontains=keyword) |
            Q(user__username__icontains=keyword) |
            Q(receiver_name__icontains=keyword) |
            Q(receiver_phone__icontains=keyword)
        )
    
    # 状态筛选
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # 分页
    paginator = Paginator(orders, 15)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES if hasattr(Order, 'STATUS_CHOICES') else [],
    }
    return render(request, 'management/order_list.html', context)


@admin_required
def order_detail(request, pk):
    """订单详情"""
    order = get_object_or_404(Order.objects.select_related('user'), pk=pk)
    items = order.items.select_related('goods').all()
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = int(new_status)
            order.save()
            messages.success(request, '订单状态已更新')
    
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'management/order_detail.html', context)


# ==================== 系统设置 ====================

@admin_required
def settings_view(request):
    """系统设置"""
    if request.method == 'POST':
        # 这里可以保存系统设置到数据库或配置文件
        # 目前简单实现，保存到session
        request.session['site_name'] = request.POST.get('site_name', '在线商城')
        request.session['site_description'] = request.POST.get('site_description', '专业的在线购物平台')
        messages.success(request, '设置已保存')
    
    context = {
        'site_name': request.session.get('site_name', '在线商城'),
        'site_description': request.session.get('site_description', '专业的在线购物平台'),
    }
    return render(request, 'management/settings.html', context)
