"""
添加模拟订单数据，用于关联商品推荐
"""
import os
import django
import random
from decimal import Decimal
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()

from django.contrib.auth.models import User
from apps.goods.models import Goods
from apps.orders.models import Order, OrderItem
from apps.users.models import Address
from django.utils import timezone

def create_mock_orders():
    """创建模拟订单"""
    
    # 获取用户
    users = User.objects.filter(is_staff=False)[:5]
    if not users:
        print("没有可用用户")
        return
    
    # 获取商品
    goods_list = list(Goods.objects.filter(is_active=True, stock__gt=0))
    if not goods_list:
        print("没有可用商品")
        return
    
    # 获取或创建地址
    for user in users:
        if not Address.objects.filter(user=user).exists():
            Address.objects.create(
                user=user,
                name=user.username,
                phone='13800138000',
                province='北京市',
                city='北京市',
                district='朝阳区',
                detail='测试地址123号',
                is_default=True
            )
    
    # 创建订单
    created = 0
    for i in range(30):  # 创建30个订单
        user = random.choice(list(users))
        address = Address.objects.filter(user=user).first()
        
        # 随机选择2-5个商品
        num_goods = random.randint(2, 5)
        order_goods = random.sample(goods_list, min(num_goods, len(goods_list)))
        
        # 计算总价
        total = Decimal('0')
        order_items = []
        
        for goods in order_goods:
            quantity = random.randint(1, 3)
            price = goods.current_price
            subtotal = Decimal(str(price)) * quantity
            total += subtotal
            
            order_items.append({
                'goods': goods,
                'quantity': quantity,
                'price': price,
            })
        
        # 创建订单
        order = Order.objects.create(
            user=user,
            total_amount=total,
            status=4,  # 已完成
            receiver_name=address.name,
            receiver_phone=address.phone,
            receiver_address=address.full_address(),
            created_at=timezone.now() - timedelta(days=random.randint(0, 30)),
            paid_at=timezone.now() - timedelta(days=random.randint(0, 29)),
            completed_at=timezone.now() - timedelta(days=random.randint(0, 28)),
        )
        
        # 创建订单商品
        for item in order_items:
            OrderItem.objects.create(
                order=order,
                goods=item['goods'],
                goods_name=item['goods'].name,
                goods_price=item['price'],
                goods_image=item['goods'].image.url if item['goods'].image else '',
                quantity=item['quantity'],
            )
        
        created += 1
        print(f"✓ 订单 {created}: {user.username} - {len(order_items)}件商品")
    
    print(f"\n完成！创建 {created} 个模拟订单")
    
    # 显示关联分析结果
    print("\n=== 关联商品分析 ===")
    from django.db.models import Count
    
    # 找出经常一起购买的商品对
    from collections import Counter
    pair_counter = Counter()
    
    orders = Order.objects.filter(status=4)
    for order in orders:
        goods_ids = list(order.items.values_list('goods_id', flat=True))
        for i in range(len(goods_ids)):
            for j in range(i+1, len(goods_ids)):
                pair = tuple(sorted([goods_ids[i], goods_ids[j]]))
                pair_counter[pair] += 1
    
    # 显示最常见的组合
    print("最常一起购买的商品组合:")
    for pair, count in pair_counter.most_common(10):
        goods1 = Goods.objects.filter(id=pair[0]).first()
        goods2 = Goods.objects.filter(id=pair[1]).first()
        if goods1 and goods2:
            print(f"  {goods1.name[:15]} + {goods2.name[:15]}: {count}次")

if __name__ == "__main__":
    create_mock_orders()
