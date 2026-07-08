from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Category, Goods
from .recommend import get_related_goods, get_bought_together, get_personal_recommendations


def index(request):
    """首页"""
    categories = Category.objects.filter(parent=None)
    goods_list = Goods.objects.filter(is_active=True).order_by('-created_at')
    
    paginator = Paginator(goods_list, 12)
    page = request.GET.get('page')
    all_goods = paginator.get_page(page)
    
    # 个性化推荐
    personal_recommendations = get_personal_recommendations(request.user, limit=4)
    
    return render(request, 'index.html', {
        'categories': categories,
        'all_goods': all_goods,
        'personal_recommendations': personal_recommendations,
    })


def goods_list(request):
    """商品列表"""
    category_id = request.GET.get('category')
    keyword = request.GET.get('keyword', '')
    sort = request.GET.get('sort', '-created_at')
    
    goods_list = Goods.objects.filter(is_active=True)
    
    if category_id:
        goods_list = goods_list.filter(category_id=category_id)
    
    if keyword:
        goods_list = goods_list.filter(
            Q(name__icontains=keyword) | Q(description__icontains=keyword)
        )
    
    # 排序
    if sort == 'price':
        goods_list = goods_list.order_by('price')
    elif sort == '-price':
        goods_list = goods_list.order_by('-price')
    elif sort == 'sales':
        goods_list = goods_list.order_by('sales')
    else:
        goods_list = goods_list.order_by('-created_at')
    
    paginator = Paginator(goods_list, 12)
    page = request.GET.get('page')
    goods = paginator.get_page(page)
    
    categories = Category.objects.filter(parent=None)
    
    return render(request, 'goods/list.html', {
        'goods': goods,
        'categories': categories,
        'keyword': keyword,
        'current_category': category_id,
        'current_sort': sort,
    })


def goods_detail(request, pk):
    """商品详情"""
    goods = get_object_or_404(Goods, pk=pk, is_active=True)
    reviews = goods.reviews.all()[:10]
    
    # 基于购买历史的关联推荐
    related_goods = get_related_goods(pk, limit=6)
    
    # 经常一起购买的商品
    bought_together = get_bought_together(pk, limit=4)
    
    # 个性化推荐
    personal_recommendations = get_personal_recommendations(request.user, limit=4)
    
    # 检查是否已收藏
    is_favorited = False
    if request.user.is_authenticated:
        from apps.favorites.models import Favorite
        is_favorited = Favorite.objects.filter(user=request.user, goods=goods).exists()
    
    return render(request, 'goods/detail.html', {
        'goods': goods,
        'reviews': reviews,
        'related_goods': related_goods,
        'bought_together': bought_together,
        'personal_recommendations': personal_recommendations,
        'is_favorited': is_favorited,
    })


def goods_search(request):
    """商品搜索"""
    keyword = request.GET.get('keyword', '')
    goods_list = Goods.objects.filter(
        Q(name__icontains=keyword) | Q(description__icontains=keyword),
        is_active=True
    )
    
    paginator = Paginator(goods_list, 12)
    page = request.GET.get('page')
    goods = paginator.get_page(page)
    
    return render(request, 'goods/list.html', {
        'goods': goods,
        'keyword': keyword,
        'categories': Category.objects.filter(parent=None),
    })


def category_list(request, pk):
    """分类商品列表"""
    category = get_object_or_404(Category, pk=pk)
    goods_list = Goods.objects.filter(category=category, is_active=True)
    
    paginator = Paginator(goods_list, 12)
    page = request.GET.get('page')
    goods = paginator.get_page(page)
    
    categories = Category.objects.filter(parent=None)
    
    return render(request, 'goods/list.html', {
        'goods': goods,
        'categories': categories,
        'current_category': pk,
    })


def bargain_list(request):
    """捡漏专区 - 临期商品"""
    from datetime import date
    today = date.today()
    
    # 获取所有临期商品（14天内到期）
    goods_list = Goods.objects.filter(
        is_active=True,
        production_date__isnull=False,
        stock__gt=0
    )
    
    # 过滤出临期商品
    bargain_goods = []
    for goods in goods_list:
        if goods.days_until_expiry is not None and 0 <= goods.days_until_expiry <= 14:
            bargain_goods.append(goods)
    
    # 按到期天数排序（越快到期越靠前）
    bargain_goods.sort(key=lambda x: x.days_until_expiry)
    
    paginator = Paginator(bargain_goods, 12)
    page = request.GET.get('page')
    goods = paginator.get_page(page)
    
    return render(request, 'goods/bargain.html', {
        'goods': goods,
    })
