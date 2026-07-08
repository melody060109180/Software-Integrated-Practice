"""
关联商品推荐模块
基于购物篮分析和协同过滤
"""
from django.db.models import Count, Q, F
from collections import defaultdict


def get_related_goods(goods_id, limit=6):
    """
    获取关联商品推荐
    优先级：购买关联 > 分类关联 > 热销推荐
    """
    from .models import Goods
    from apps.orders.models import OrderItem
    
    related_ids = set()
    related_scores = defaultdict(float)
    
    # 方法1: 基于购买历史的关联（购物篮分析）
    # 找出购买过该商品的订单
    order_ids = OrderItem.objects.filter(
        goods_id=goods_id
    ).values_list('order_id', flat=True).distinct()
    
    if order_ids:
        # 找出这些订单中的其他商品，统计共购次数
        co_purchased = OrderItem.objects.filter(
            order_id__in=order_ids
        ).exclude(
            goods_id=goods_id
        ).values(
            'goods_id'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:20]
        
        for item in co_purchased:
            goods_id_related = item['goods_id']
            count = item['count']
            # 共购次数越多，关联度越高
            related_scores[goods_id_related] += count * 3.0
    
    # 方法2: 同分类商品（作为补充）
    current_goods = Goods.objects.filter(id=goods_id).first()
    if current_goods and current_goods.category:
        same_category = Goods.objects.filter(
            category=current_goods.category,
            is_active=True,
            stock__gt=0
        ).exclude(id=goods_id).values_list('id', flat=True)[:10]
        
        for cid in same_category:
            if cid not in related_scores:
                related_scores[cid] += 1.0
    
    # 方法3: 热销商品（兜底）
    if len(related_scores) < limit:
        hot_goods = Goods.objects.filter(
            is_active=True,
            stock__gt=0
        ).exclude(
            id=goods_id
        ).order_by('-sales')[:10].values_list('id', flat=True)
        
        for hid in hot_goods:
            if hid not in related_scores:
                related_scores[hid] += 0.5
    
    # 按分数排序，取前N个
    sorted_ids = sorted(related_scores.keys(), 
                       key=lambda x: related_scores[x], 
                       reverse=True)[:limit]
    
    if not sorted_ids:
        # 如果没有关联商品，返回同分类商品
        if current_goods and current_goods.category:
            return Goods.objects.filter(
                category=current_goods.category,
                is_active=True,
                stock__gt=0
            ).exclude(id=goods_id)[:limit]
        return Goods.objects.filter(
            is_active=True,
            stock__gt=0
        ).exclude(id=goods_id).order_by('-sales')[:limit]
    
    # 保持排序顺序返回
    goods_dict = {g.id: g for g in Goods.objects.filter(id__in=sorted_ids)}
    return [goods_dict[gid] for gid in sorted_ids if gid in goods_dict]


def get_bought_together(goods_id, limit=4):
    """
    获取"经常一起购买"的商品
    专门用于购物篮分析展示
    """
    from apps.orders.models import OrderItem
    
    # 找出购买过该商品的订单
    order_ids = OrderItem.objects.filter(
        goods_id=goods_id
    ).values_list('order_id', flat=True).distinct()
    
    if not order_ids:
        return []
    
    # 统计共购次数
    co_purchased = OrderItem.objects.filter(
        order_id__in=order_ids
    ).exclude(
        goods_id=goods_id
    ).values(
        'goods_id', 'goods_name', 'goods_price'
    ).annotate(
        count=Count('id'),
        total_quantity=Count('quantity')
    ).order_by('-count')[:limit]
    
    return list(co_purchased)


def get_personal_recommendations(user, limit=8):
    """
    个性化推荐（基于用户购买历史）
    """
    from .models import Goods
    from apps.orders.models import Order, OrderItem
    
    if not user.is_authenticated:
        # 未登录返回热销商品
        return Goods.objects.filter(
            is_active=True, stock__gt=0
        ).order_by('-sales')[:limit]
    
    # 获取用户购买过的商品ID
    purchased_ids = OrderItem.objects.filter(
        order__user=user,
        order__status__in=[2, 3, 4]  # 已支付、已发货、已完成
    ).values_list('goods_id', flat=True).distinct()
    
    if not purchased_ids:
        return Goods.objects.filter(
            is_active=True, stock__gt=0
        ).order_by('-sales')[:limit]
    
    # 获取用户购买过的分类
    from .models import Category
    purchased_categories = Goods.objects.filter(
        id__in=purchased_ids
    ).values_list('category_id', flat=True).distinct()
    
    # 推荐同分类但未购买的商品
    recommendations = Goods.objects.filter(
        category_id__in=purchased_categories,
        is_active=True,
        stock__gt=0
    ).exclude(
        id__in=purchased_ids
    ).order_by('-sales')[:limit]
    
    # 如果不够，补充热销商品
    if recommendations.count() < limit:
        remaining = limit - recommendations.count()
        existing_ids = list(purchased_ids) + list(recommendations.values_list('id', flat=True))
        hot_goods = Goods.objects.filter(
            is_active=True,
            stock__gt=0
        ).exclude(
            id__in=existing_ids
        ).order_by('-sales')[:remaining]
        
        from itertools import chain
        recommendations = list(chain(recommendations, hot_goods))
    
    return recommendations
