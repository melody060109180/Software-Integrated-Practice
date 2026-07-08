from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import Merchant, MerchantGoods
from .forms import MerchantProfileForm, GoodsForm, MerchantGoodsForm
from apps.goods.models import Goods, Category
from apps.orders.models import Order, OrderItem
from apps.riders.models import Rider
from apps.orders.capacity import check_capacity, get_order_weight, get_order_volume, get_order_items_info


def _admin_required(user):
    """检查用户是否是管理员（staff）"""
    return user.is_staff


@login_required
def dashboard(request):
    """管理员后台首页 - 数据统计"""
    if not request.user.is_staff:
        messages.error(request, '无权访问！')
        return redirect('goods:list')

    today = timezone.now().date()
    month_start = today.replace(day=1)

    # 商品统计
    total_goods = Goods.objects.count()
    active_goods = Goods.objects.filter(is_active=True).count()

    # 订单统计
    total_orders = Order.objects.count()
    month_orders = Order.objects.filter(created_at__date__gte=month_start).count()

    # 销售统计
    total_sales = OrderItem.objects.filter(
        order__status__in=[2, 3, 4]
    ).aggregate(total=Sum('quantity'))['total'] or 0

    month_sales = OrderItem.objects.filter(
        order__status__in=[2, 3, 4],
        order__created_at__date__gte=month_start
    ).aggregate(total=Sum('quantity'))['total'] or 0

    # 收入统计
    total_revenue = OrderItem.objects.filter(
        order__status__in=[2, 3, 4]
    ).aggregate(total=Sum(F('goods_price') * F('quantity')))['total'] or 0

    month_revenue = OrderItem.objects.filter(
        order__status__in=[2, 3, 4],
        order__created_at__date__gte=month_start
    ).aggregate(total=Sum(F('goods_price') * F('quantity')))['total'] or 0

    # 骑手统计
    total_riders = Rider.objects.count()
    available_riders = Rider.objects.filter(is_available=True, is_active=True).count()

    # 最近订单
    recent_orders = Order.objects.all().order_by('-created_at')[:5]

    # 获取或创建店铺信息
    merchant, _ = Merchant.objects.get_or_create(
        user=request.user,
        defaults={
            'shop_name': '默认店铺',
            'contact_phone': '',
            'address': '',
        }
    )

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
        'total_riders': total_riders,
        'available_riders': available_riders,
        'recent_orders': recent_orders,
    }
    return render(request, 'merchants/dashboard.html', context)


@login_required
def profile(request):
    """商家信息"""
    merchant, _ = Merchant.objects.get_or_create(
        user=request.user,
        defaults={'shop_name': '默认店铺', 'contact_phone': '', 'address': ''}
    )
    return render(request, 'merchants/profile.html', {'merchant': merchant})


@login_required
def profile_edit(request):
    """编辑商家信息"""
    merchant, _ = Merchant.objects.get_or_create(
        user=request.user,
        defaults={'shop_name': '默认店铺', 'contact_phone': '', 'address': ''}
    )
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
    """商品列表（管理员）"""
    if not request.user.is_staff:
        messages.error(request, '无权访问！')
        return redirect('goods:list')

    keyword = request.GET.get('keyword', '')
    status = request.GET.get('status', '')

    goods = Goods.objects.select_related('category').all()

    if keyword:
        goods = goods.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))

    if status == 'active':
        goods = goods.filter(is_active=True)
    elif status == 'inactive':
        goods = goods.filter(is_active=False)

    return render(request, 'merchants/goods_list.html', {
        'goods_list': goods,
        'keyword': keyword,
        'status': status,
    })


@login_required
def goods_add(request):
    """添加商品"""
    if not request.user.is_staff:
        messages.error(request, '无权访问！')
        return redirect('goods:list')

    if request.method == 'POST':
        goods_form = GoodsForm(request.POST, request.FILES)
        if goods_form.is_valid():
            goods_form.save()
            messages.success(request, '商品添加成功！')
            return redirect('merchants:goods_list')
    else:
        goods_form = GoodsForm()

    return render(request, 'merchants/goods_form.html', {
        'goods_form': goods_form,
        'title': '添加商品',
    })


@login_required
def goods_edit(request, pk):
    """编辑商品"""
    if not request.user.is_staff:
        messages.error(request, '无权访问！')
        return redirect('goods:list')

    goods = get_object_or_404(Goods, pk=pk)

    if request.method == 'POST':
        goods_form = GoodsForm(request.POST, request.FILES, instance=goods)
        if goods_form.is_valid():
            goods_form.save()
            messages.success(request, '商品更新成功！')
            return redirect('merchants:goods_list')
    else:
        goods_form = GoodsForm(instance=goods)

    return render(request, 'merchants/goods_form.html', {
        'goods_form': goods_form,
        'title': '编辑商品',
    })


@login_required
def goods_delete(request, pk):
    """删除商品"""
    if not request.user.is_staff:
        messages.error(request, '无权访问！')
        return redirect('goods:list')

    goods = get_object_or_404(Goods, pk=pk)
    if request.method == 'POST':
        goods.delete()
        messages.success(request, '商品已删除！')
    return redirect('merchants:goods_list')


@login_required
def goods_toggle(request, pk):
    """上下架商品"""
    if request.method != 'POST':
        return redirect('merchants:goods_list')
    if not request.user.is_staff:
        messages.error(request, '无权访问！')
        return redirect('goods:list')

    goods = get_object_or_404(Goods, pk=pk)
    goods.is_active = not goods.is_active
    goods.save()

    status = '上架' if goods.is_active else '下架'
    messages.success(request, f'商品已{status}！')
    return redirect('merchants:goods_list')


@login_required
def order_list(request):
    """订单列表（管理员）"""
    if not request.user.is_staff:
        messages.error(request, '无权访问！')
        return redirect('goods:list')

    status = request.GET.get('status', '')
    orders = Order.objects.all().order_by('-created_at')

    if status:
        orders = orders.filter(status=status)

    return render(request, 'merchants/order_list.html', {
        'orders': orders,
        'status': status,
    })


@login_required
def order_detail(request, pk):
    """订单详情（管理员）"""
    if not request.user.is_staff:
        messages.error(request, '无权访问！')
        return redirect('goods:list')

    order = get_object_or_404(Order, pk=pk)
    idle_riders = Rider.objects.filter(is_available=True, is_active=True)
    
    # 防爆单检查
    is_safe, capacity_message, capacity_details = check_capacity(order)

    return render(request, 'merchants/order_detail.html', {
        'order': order,
        'idle_riders': idle_riders,
        'is_safe': is_safe,
        'capacity_message': capacity_message,
        'capacity_details': capacity_details,
    })


@login_required
def order_ship(request, pk):
    """发货 + 自动派单"""
    if request.method != 'POST':
        return redirect('merchants:order_detail', pk=pk)
    if not request.user.is_staff:
        messages.error(request, '无权访问！')
        return redirect('goods:list')

    order = get_object_or_404(Order, pk=pk)

    if order.status == 2:  # 已支付
        order.status = 3  # 已发货
        order.shipped_at = timezone.now()

        # 尝试自动派单
        idle_riders = Rider.objects.filter(is_available=True, is_active=True).annotate(
            active_deliveries=Count('deliveries', filter=Q(deliveries__delivery_status__in=[1, 2]))
        ).order_by('active_deliveries')

        if idle_riders.exists():
            rider = idle_riders.first()
            order.rider = rider
            order.delivery_status = 1  # 待配送
            order.assigned_at = timezone.now()
            messages.success(request, f'订单已发货并指派给骑手 {rider.real_name}')
        else:
            messages.warning(request, '订单已发货，暂无空闲骑手，请手动指派')

        order.save()
    else:
        messages.error(request, '该订单无法发货')

    return redirect('merchants:order_detail', pk=pk)


@login_required
def rider_list(request):
    """骑手列表（管理员）"""
    if not request.user.is_staff:
        messages.error(request, '无权访问！')
        return redirect('goods:list')

    from apps.riders.models import Rider
    riders = Rider.objects.annotate(
        active_deliveries=Count('deliveries', filter=Q(deliveries__delivery_status__in=[1, 2]))
    ).order_by('-created_at')

    return render(request, 'merchants/rider_list.html', {'riders': riders})


@login_required
def assign_rider(request, pk):
    """手动指派骑手"""
    if not request.user.is_staff:
        messages.error(request, '无权访问！')
        return redirect('goods:list')

    order = get_object_or_404(Order, pk=pk)
    from apps.riders.models import Rider

    if request.method == 'POST':
        rider_id = request.POST.get('rider_id')
        if rider_id:
            rider = get_object_or_404(Rider, pk=rider_id, is_available=True, is_active=True)
            order.rider = rider
            order.delivery_status = 1  # 待配送
            order.assigned_at = timezone.now()
            order.save()
            messages.success(request, f'已指派骑手 {rider.real_name}')
        else:
            messages.error(request, '请选择骑手')
        return redirect('merchants:order_detail', pk=pk)

    idle_riders = Rider.objects.filter(is_available=True, is_active=True)
    return render(request, 'merchants/assign_rider.html', {
        'order': order,
        'idle_riders': idle_riders,
    })


@login_required
def auto_assign(request, pk):
    """自动派单"""
    if request.method != 'POST':
        return redirect('merchants:order_detail', pk=pk)
    if not request.user.is_staff:
        messages.error(request, '无权访问！')
        return redirect('goods:list')

    order = get_object_or_404(Order, pk=pk)
    from apps.riders.models import Rider

    idle_riders = Rider.objects.filter(is_available=True, is_active=True).annotate(
        active_deliveries=Count('deliveries', filter=Q(deliveries__delivery_status__in=[1, 2]))
    ).order_by('active_deliveries')

    if idle_riders.exists():
        rider = idle_riders.first()
        order.rider = rider
        order.delivery_status = 1
        order.assigned_at = timezone.now()
        order.save()
        messages.success(request, f'已自动指派给骑手 {rider.real_name}')
    else:
        messages.warning(request, '暂无空闲骑手')

    return redirect('merchants:order_detail', pk=pk)
