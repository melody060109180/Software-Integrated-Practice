from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem
from apps.goods.models import Goods


@login_required
def cart_detail(request):
    """购物车详情"""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart.html', {'cart': cart})


@login_required
def cart_add(request):
    """添加商品到购物车"""
    if request.method == 'POST':
        goods_id = request.POST.get('goods_id')
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1
        
        goods = get_object_or_404(Goods, pk=goods_id, is_active=True)
        
        if quantity > goods.stock:
            messages.error(request, '库存不足！')
            return redirect('goods:detail', pk=goods_id)
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, goods=goods,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > goods.stock:
                messages.error(request, '库存不足！')
                return redirect('goods:detail', pk=goods_id)
            cart_item.save()
        
        messages.success(request, '已添加到购物车！')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'cart_count': cart.total_quantity,
                'message': '已添加到购物车'
            })
        
        return redirect('cart:detail')
    
    return redirect('goods:list')


@login_required
def cart_update(request, item_id):
    """更新购物车商品数量"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, '商品已从购物车移除！')
        elif quantity > cart_item.goods.stock:
            messages.error(request, '库存不足！')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, '购物车已更新！')
    
    return redirect('cart:detail')


@login_required
def cart_remove(request, item_id):
    """从购物车移除商品"""
    if request.method != 'POST':
        return redirect('cart:detail')
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, '商品已从购物车移除！')
    return redirect('cart:detail')


@login_required
def cart_clear(request):
    """清空购物车"""
    if request.method == 'POST':
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        messages.success(request, '购物车已清空！')
    return redirect('cart:detail')
