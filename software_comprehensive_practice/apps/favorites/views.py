from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Favorite
from apps.goods.models import Goods


@login_required
def toggle_favorite(request, goods_id):
    """收藏/取消收藏商品"""
    if request.method != 'POST':
        return redirect('goods:detail', pk=goods_id)
    
    goods = get_object_or_404(Goods, pk=goods_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, goods=goods)
    
    if not created:
        # 已收藏，取消收藏
        favorite.delete()
        message = '已取消收藏'
        is_favorited = False
    else:
        # 新收藏
        message = '收藏成功'
        is_favorited = True
    
    # 如果是AJAX请求，返回JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'message': message,
        })
    
    messages.success(request, message)
    return redirect('goods:detail', pk=goods_id)


@login_required
def favorite_list(request):
    """收藏列表"""
    favorites = Favorite.objects.filter(user=request.user).select_related('goods', 'goods__category')
    
    # 获取每个商品的当前价格
    favorites_with_price = []
    for fav in favorites:
        favorites_with_price.append({
            'id': fav.id,
            'goods': fav.goods,
            'created_at': fav.created_at,
        })
    
    return render(request, 'favorites/list.html', {
        'favorites': favorites_with_price,
    })


@login_required
def remove_favorite(request, pk):
    """从收藏列表移除"""
    if request.method != 'POST':
        return redirect('favorites:list')
    
    favorite = get_object_or_404(Favorite, pk=pk, user=request.user)
    goods_id = favorite.goods.id
    favorite.delete()
    
    messages.success(request, '已取消收藏')
    return redirect('favorites:list')
