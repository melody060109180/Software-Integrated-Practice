"""
为现有商品添加保质期数据
模拟不同保质期状态的商品
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()

from apps.goods.models import Goods

# 为不同分类的商品设置不同的生产日期和保质期
CATEGORY_CONFIG = {
    '电子产品': {'shelf_life': 730, 'days_ago_range': (30, 180)},
    '数码产品': {'shelf_life': 730, 'days_ago_range': (30, 180)},
    '服装': {'shelf_life': 1095, 'days_ago_range': (30, 90)},
    '服装鞋帽': {'shelf_life': 1095, 'days_ago_range': (30, 90)},
    '生鲜果蔬': {'shelf_life': 7, 'days_ago_range': (1, 10)},
    '食品': {'shelf_life': 180, 'days_ago_range': (30, 150)},
    '食品饮料': {'shelf_life': 365, 'days_ago_range': (30, 300)},
    '家居日用': {'shelf_life': 1095, 'days_ago_range': (30, 180)},
    '美妆护肤': {'shelf_life': 1095, 'days_ago_range': (30, 365)},
}

# 特定商品的特殊配置（模拟临期状态）
SPECIFIC_CONFIG = {
    '可口可乐 330ml*24罐': {'shelf_life': 365, 'days_ago': 350},  # 15天后过期
    '红牛维生素功能饮料 250ml*24': {'shelf_life': 365, 'days_ago': 360},  # 5天后过期
    '王老吉凉茶 310ml*24罐': {'shelf_life': 365, 'days_ago': 362},  # 3天后过期
    '智利进口车厘子 2斤': {'shelf_life': 7, 'days_ago': 6},  # 1天后过期
    '海南三亚芒果 5斤': {'shelf_life': 7, 'days_ago': 5},  # 2天后过期
    '泰国金枕头榴莲 3-4斤': {'shelf_life': 7, 'days_ago': 4},  # 3天后过期
    '有机蔬菜礼盒 10种': {'shelf_life': 5, 'days_ago': 5},  # 已过期
    '蒙牛纯甄酸奶 200g*12': {'shelf_life': 180, 'days_ago': 170},  # 10天后过期
    '三只松鼠猪肉脯 200g': {'shelf_life': 180, 'days_ago': 175},  # 5天后过期
    '良品铺子坚果大礼包 1.68kg': {'shelf_life': 180, 'days_ago': 168},  # 12天后过期
    '星巴克挂耳咖啡 10包': {'shelf_life': 365, 'days_ago': 358},  # 7天后过期
    '雀巢咖啡即饮 268ml*12': {'shelf_life': 365, 'days_ago': 362},  # 3天后过期
    '元气森林气泡水 480ml*12': {'shelf_life': 365, 'days_ago': 355},  # 10天后过期
}

import random

def run():
    goods_list = Goods.objects.all()
    updated = 0
    
    for goods in goods_list:
        # 优先使用特定配置
        if goods.name in SPECIFIC_CONFIG:
            config = SPECIFIC_CONFIG[goods.name]
            production_date = date.today() - timedelta(days=config['days_ago'])
            goods.production_date = production_date
            goods.shelf_life_days = config['shelf_life']
            goods.save()
            updated += 1
            print(f"✓ [特定] {goods.name[:25]}... | 生产: {production_date} | 保质期: {config['shelf_life']}天")
            continue
        
        # 根据分类设置
        if goods.category and goods.category.name in CATEGORY_CONFIG:
            config = CATEGORY_CONFIG[goods.category.name]
            days_ago = random.randint(*config['days_ago_range'])
            production_date = date.today() - timedelta(days=days_ago)
            goods.production_date = production_date
            goods.shelf_life_days = config['shelf_life']
            goods.save()
            updated += 1
            print(f"✓ [分类] {goods.name[:25]}... | 生产: {production_date} | 保质期: {config['shelf_life']}天")
        else:
            # 默认设置
            goods.shelf_life_days = 365
            goods.save()
            updated += 1
            print(f"✓ [默认] {goods.name[:25]}... | 保质期: 365天")
    
    print(f"\n完成！共更新 {updated} 个商品")
    
    # 显示临期商品统计
    print("\n=== 临期商品统计 ===")
    near_expiry = Goods.objects.filter(is_active=True)
    expired_count = 0
    soon_expire = 0
    normal = 0
    
    for g in near_expiry:
        days = g.days_until_expiry
        if days is not None:
            if days < 0:
                expired_count += 1
            elif days <= 14:
                soon_expire += 1
            else:
                normal += 1
    
    print(f"已过期: {expired_count}")
    print(f"14天内临期: {soon_expire}")
    print(f"正常: {normal}")

if __name__ == "__main__":
    run()
