from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Order, OrderItem
from apps.cart.models import Cart
from apps.users.models import Address


@login_required
def checkout(request):
    """结算页面"""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('goods').all()
    
    if not cart_items:
        messages.warning(request, '购物车为空！')
        return redirect('cart:detail')
    
    # 检查库存
    for item in cart_items:
        if item.quantity > item.goods.stock:
            messages.error(request, f'{item.goods.name}库存不足！')
            return redirect('cart:detail')
    
    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()
    
    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total_price': cart.total_price,
        'addresses': addresses,
        'default_address': default_address,
    })


@login_required
def order_list(request):
    """订单列表"""
    status = request.GET.get('status')
    orders = Order.objects.filter(user=request.user)
    
    if status:
        orders = orders.filter(status=status)
    
    return render(request, 'orders/list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    """订单详情"""
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})


@login_required
def order_cancel(request, pk):
    """取消订单"""
    if request.method != 'POST':
        return redirect('orders:detail', pk=pk)
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.can_cancel():
        order.status = 5
        order.save()
        # 恢复库存
        for item in order.items.all():
            if item.goods:
                item.goods.stock += item.quantity
                item.goods.save()
        messages.success(request, '订单已取消！')
    else:
        messages.error(request, '该订单无法取消！')
    return redirect('orders:detail', pk=pk)


@login_required
def order_confirm(request, pk):
    """确认收货"""
    if request.method != 'POST':
        return redirect('orders:detail', pk=pk)
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.can_confirm():
        order.status = 4
        order.completed_at = timezone.now()
        order.save()
        messages.success(request, '已确认收货！')
    else:
        messages.error(request, '该订单无法确认收货！')
    return redirect('orders:detail', pk=pk)


@login_required
def create_order(request):
    """创建订单"""
    if request.method == 'POST':
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.select_related('goods').all()
        
        if not cart_items:
            messages.warning(request, '购物车为空！')
            return redirect('cart:detail')
        
        address_id = request.POST.get('address_id')
        address = get_object_or_404(Address, pk=address_id, user=request.user)
        
        # 创建订单
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.total_price,
            receiver_name=address.name,
            receiver_phone=address.phone,
            receiver_address=address.full_address(),
            remark=request.POST.get('remark', ''),
        )
        
        # 创建订单商品并扣减库存
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                goods=item.goods,
                goods_name=item.goods.name,
                goods_price=item.goods.price,
                goods_image=item.goods.image.url if item.goods.image else '',
                quantity=item.quantity,
            )
            # 扣减库存
            item.goods.stock -= item.quantity
            item.goods.save()
        
        # 清空购物车
        cart.items.all().delete()
        
        messages.success(request, '订单创建成功！')
        return redirect('payments:pay', order_id=order.pk)
    
    return redirect('cart:detail')
