from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, Goods


def index(request):
    """首页"""
    categories = Category.objects.filter(parent=None)
    all_goods = Goods.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'index.html', {
        'categories': categories,
        'all_goods': all_goods,
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
    related_goods = Goods.objects.filter(
        category=goods.category, is_active=True
    ).exclude(pk=pk)[:4]
    
    return render(request, 'goods/detail.html', {
        'goods': goods,
        'reviews': reviews,
        'related_goods': related_goods,
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
