from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Review
from apps.goods.models import Goods
from apps.orders.models import Order


@login_required
def review_add(request, goods_id):
    """添加评价"""
    goods = get_object_or_404(Goods, pk=goods_id)
    
    # 检查是否已购买
    if not Order.objects.filter(
        user=request.user,
        items__goods=goods,
        status__in=[2, 3, 4]
    ).exists():
        messages.error(request, '只有购买过该商品的用户才能评价！')
        return redirect('goods:detail', pk=goods_id)
    
    # 检查是否已评价
    if Review.objects.filter(user=request.user, goods=goods).exists():
        messages.warning(request, '您已经评价过该商品！')
        return redirect('goods:detail', pk=goods_id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        content = request.POST.get('content', '')
        
        # 获取最近的订单
        order = Order.objects.filter(
            user=request.user,
            items__goods=goods,
            status__in=[2, 3, 4]
        ).first()
        
        if order:
            Review.objects.create(
                user=request.user,
                goods=goods,
                order=order,
                rating=rating,
                content=content,
            )
            messages.success(request, '评价成功！')
            return redirect('goods:detail', pk=goods_id)
        else:
            messages.error(request, '未找到有效订单，无法评价！')
            return redirect('goods:detail', pk=goods_id)
    
    return render(request, 'reviews/add.html', {'goods': goods})


@login_required
def review_list(request, goods_id):
    """评价列表"""
    goods = get_object_or_404(Goods, pk=goods_id)
    reviews = Review.objects.filter(goods=goods).select_related('user')
    
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')
    reviews = paginator.get_page(page)
    
    return render(request, 'reviews/list.html', {
        'goods': goods,
        'reviews': reviews,
    })


@login_required
def review_delete(request, pk):
    """删除评价"""
    if request.method != 'POST':
        return redirect('goods:list')
    review = get_object_or_404(Review, pk=pk, user=request.user)
    goods_id = review.goods.pk
    review.delete()
    messages.success(request, '评价已删除！')
    return redirect('goods:detail', pk=goods_id)
