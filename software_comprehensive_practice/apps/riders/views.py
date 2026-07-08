from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from .models import Rider
from .forms import RiderRegisterForm, RiderProfileForm
from apps.orders.models import Order
from apps.orders.capacity import check_capacity, get_order_weight, get_order_volume, get_order_items_info


def _get_rider_or_redirect(request):
    """获取当前用户的骑手资料，没有则重定向到首页"""
    try:
        return Rider.objects.get(user=request.user)
    except Rider.DoesNotExist:
        messages.error(request, '您还没有骑手资料，请先注册骑手！')
        return None


def rider_register(request):
    """骑手注册"""
    if request.method == 'POST':
        form = RiderRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '骑手注册成功！')
            return redirect('riders:dashboard')
    else:
        form = RiderRegisterForm()
    return render(request, 'riders/register.html', {'form': form})


@login_required
def dashboard(request):
    """骑手主页"""
    rider = _get_rider_or_redirect(request)
    if rider is None:
        return redirect('goods:list')
    today = timezone.now().date()

    # 今日完成
    today_completed = rider.deliveries.filter(
        delivery_status=3, delivered_at__date=today
    ).count()
    # 待配送（已指派，未接单）
    pending = rider.deliveries.filter(delivery_status=1).count()
    # 配送中
    delivering = rider.deliveries.filter(delivery_status=2).count()
    # 总完成
    total_completed = rider.deliveries.filter(delivery_status=3).count()

    context = {
        'rider': rider,
        'today_completed': today_completed,
        'pending': pending,
        'delivering': delivering,
        'total_completed': total_completed,
    }
    return render(request, 'riders/dashboard.html', context)


@login_required
def delivery_list(request):
    """配送任务列表（待配送 + 配送中）"""
    rider = _get_rider_or_redirect(request)
    if rider is None:
        return redirect('goods:list')
    orders = Order.objects.filter(
        rider=rider, delivery_status__in=[1, 2]
    ).order_by('-assigned_at')
    return render(request, 'riders/delivery_list.html', {'orders': orders})


@login_required
def delivery_detail(request, pk):
    """配送详情"""
    rider = _get_rider_or_redirect(request)
    if rider is None:
        return redirect('goods:list')
    order = get_object_or_404(Order, pk=pk, rider=rider)
    
    # 防爆单检查
    is_safe, capacity_message, capacity_details = check_capacity(order)
    order_items_info = get_order_items_info(order)
    
    context = {
        'order': order,
        'is_safe': is_safe,
        'capacity_message': capacity_message,
        'capacity_details': capacity_details,
        'order_items_info': order_items_info,
    }
    return render(request, 'riders/delivery_detail.html', context)


@login_required
def accept_delivery(request, pk):
    """骑手接受配送任务"""
    if request.method != 'POST':
        return redirect('riders:delivery_detail', pk=pk)
    rider = _get_rider_or_redirect(request)
    if rider is None:
        return redirect('goods:list')
    order = get_object_or_404(Order, pk=pk, rider=rider, delivery_status=1)
    order.delivery_status = 2  # 配送中
    order.save()
    messages.success(request, '已接受配送任务！')
    return redirect('riders:delivery_detail', pk=pk)


@login_required
def complete_delivery(request, pk):
    """骑手完成配送"""
    if request.method != 'POST':
        return redirect('riders:delivery_detail', pk=pk)
    rider = _get_rider_or_redirect(request)
    if rider is None:
        return redirect('goods:list')
    order = get_object_or_404(Order, pk=pk, rider=rider, delivery_status=2)
    order.delivery_status = 3  # 已送达
    order.delivered_at = timezone.now()
    order.status = 4  # 已完成
    order.completed_at = timezone.now()
    order.save()
    messages.success(request, '配送完成！')
    return redirect('riders:delivery_detail', pk=pk)


@login_required
def delivery_history(request):
    """配送历史"""
    rider = _get_rider_or_redirect(request)
    if rider is None:
        return redirect('goods:list')
    orders = Order.objects.filter(
        rider=rider, delivery_status=3
    ).order_by('-delivered_at')
    return render(request, 'riders/history.html', {'orders': orders})


@login_required
def toggle_availability(request):
    """切换空闲状态"""
    if request.method != 'POST':
        return redirect('riders:dashboard')
    rider = _get_rider_or_redirect(request)
    if rider is None:
        return redirect('goods:list')
    rider.is_available = not rider.is_available
    rider.save()
    status = '空闲' if rider.is_available else '忙碌'
    messages.success(request, f'状态已切换为：{status}')
    return redirect('riders:dashboard')


@login_required
def profile(request):
    """个人资料"""
    rider = _get_rider_or_redirect(request)
    if rider is None:
        return redirect('goods:list')
    return render(request, 'riders/profile.html', {'rider': rider})


@login_required
def profile_edit(request):
    """编辑个人资料"""
    rider = _get_rider_or_redirect(request)
    if rider is None:
        return redirect('goods:list')
    if request.method == 'POST':
        form = RiderProfileForm(request.POST, instance=rider)
        if form.is_valid():
            form.save()
            messages.success(request, '资料更新成功！')
            return redirect('riders:profile')
    else:
        form = RiderProfileForm(instance=rider)
    return render(request, 'riders/profile_edit.html', {'form': form, 'rider': rider})


@login_required
def rider_logout(request):
    """骑手登出"""
    if request.method != 'POST':
        return redirect('riders:dashboard')
    logout(request)
    messages.success(request, '已退出登录！')
    return redirect('goods:list')
