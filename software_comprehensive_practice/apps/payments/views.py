from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Payment
from apps.orders.models import Order


@login_required
def pay(request, order_id):
    """支付页面"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    if order.status != 1:
        messages.warning(request, '该订单无需支付！')
        return redirect('orders:detail', pk=order_id)
    
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={'amount': order.total_amount}
    )
    
    return render(request, 'payments/pay.html', {
        'order': order,
        'payment': payment,
    })


@login_required
def payment_success(request, order_id):
    """支付成功"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    payment = get_object_or_404(Payment, order=order)

    # 保存支付方式
    method = request.POST.get('payment_method')
    if method and method.isdigit():
        payment.method = int(method)

    # 模拟支付成功
    payment.status = 2
    payment.paid_at = timezone.now()
    payment.save()

    order.status = 2
    order.paid_at = timezone.now()
    order.save()

    messages.success(request, '支付成功！')
    return redirect('orders:detail', pk=order_id)


@login_required
def payment_cancel(request, order_id):
    """取消支付"""
    messages.info(request, '支付已取消！')
    return redirect('orders:detail', pk=order_id)
