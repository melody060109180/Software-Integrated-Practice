"""
为商品添加重量和体积数据
"""
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()

from apps.goods.models import Goods

# 不同分类的默认重量和尺寸
CATEGORY_DEFAULTS = {
    '电子产品': {'weight': 0.5, 'length': 25, 'width': 15, 'height': 8},
    '数码产品': {'weight': 0.3, 'length': 20, 'width': 12, 'height': 6},
    '服装': {'weight': 0.3, 'length': 30, 'width': 25, 'height': 3},
    '服装鞋帽': {'weight': 0.8, 'length': 35, 'width': 25, 'height': 12},
    '生鲜果蔬': {'weight': 2.0, 'length': 30, 'width': 25, 'height': 15},
    '食品': {'weight': 1.0, 'length': 25, 'width': 20, 'height': 15},
    '食品饮料': {'weight': 5.0, 'length': 40, 'width': 30, 'height': 25},
    '家居日用': {'weight': 3.0, 'length': 40, 'width': 30, 'height': 20},
    '美妆护肤': {'weight': 0.3, 'length': 15, 'width': 10, 'height': 8},
}

# 特定商品的特殊配置
SPECIFIC_CONFIG = {
    'iPhone 15 Pro Max 256GB': {'weight': 0.23, 'length': 16, 'width': 8, 'height': 2},
    'MacBook Pro 14英寸 M3': {'weight': 1.6, 'length': 35, 'width': 25, 'height': 2},
    'iPad Air 5 64GB': {'weight': 0.46, 'length': 25, 'width': 18, 'height': 1},
    'AirPods Pro 2': {'weight': 0.05, 'length': 10, 'width': 8, 'height': 3},
    '华为 Mate 60 Pro': {'weight': 0.22, 'length': 16, 'width': 8, 'height': 2},
    '小米14 Ultra': {'weight': 0.23, 'length': 16, 'width': 8, 'height': 2},
    '三星 Galaxy S24 Ultra': {'weight': 0.23, 'length': 16, 'width': 8, 'height': 2},
    '索尼 WH-1000XM5': {'weight': 0.25, 'length': 25, 'width': 20, 'height': 8},
    '佳能 EOS R6 Mark II': {'weight': 0.7, 'length': 14, 'width': 10, 'height': 8},
    '大疆 Mini 4 Pro': {'weight': 0.25, 'length': 15, 'width': 10, 'height': 6},
    'Switch OLED白色': {'weight': 0.42, 'length': 24, 'width': 10, 'height': 3},
    'Kindle Paperwhite 5': {'weight': 0.21, 'length': 17, 'width': 12, 'height': 1},
    'Apple Watch Series 9': {'weight': 0.05, 'length': 10, 'width': 8, 'height': 3},
    '华为 Watch GT 4': {'weight': 0.05, 'length': 10, 'width': 8, 'height': 3},
    # 饮料
    '可口可乐 330ml*24罐': {'weight': 8.0, 'length': 45, 'width': 30, 'height': 25},
    '红牛维生素功能饮料 250ml*24': {'weight': 6.5, 'length': 40, 'width': 28, 'height': 22},
    '王老吉凉茶 310ml*24罐': {'weight': 8.5, 'length': 45, 'width': 30, 'height': 25},
    '农夫山泉天然水 550ml*24': {'weight': 13.0, 'length': 50, 'width': 35, 'height': 30},
    '伊利金典纯牛奶 250ml*12': {'weight': 3.5, 'length': 35, 'width': 25, 'height': 15},
    '蒙牛纯甄酸奶 200g*12': {'weight': 2.8, 'length': 30, 'width': 22, 'height': 12},
    # 食品
    '良品铺子坚果大礼包 1.68kg': {'weight': 2.0, 'length': 40, 'width': 30, 'height': 15},
    '三只松鼠猪肉脯 200g': {'weight': 0.25, 'length': 25, 'width': 18, 'height': 3},
    '百草味麻花 500g': {'weight': 0.55, 'length': 30, 'width': 20, 'height': 10},
    '星巴克挂耳咖啡 10包': {'weight': 0.15, 'length': 20, 'width': 15, 'height': 5},
    # 生鲜
    '智利进口车厘子 2斤': {'weight': 1.0, 'length': 25, 'width': 20, 'height': 10},
    '新疆阿克苏苹果 5斤': {'weight': 2.5, 'length': 30, 'width': 25, 'height': 15},
    '泰国金枕头榴莲 3-4斤': {'weight': 2.0, 'length': 30, 'width': 25, 'height': 20},
    '海南三亚芒果 5斤': {'weight': 2.5, 'length': 35, 'width': 25, 'height': 15},
    '澳洲安格斯牛排 2片装': {'weight': 0.5, 'length': 25, 'width': 18, 'height': 3},
    '三文鱼刺身 500g': {'weight': 0.55, 'length': 25, 'width': 18, 'height': 3},
}

def run():
    goods_list = Goods.objects.all()
    updated = 0
    
    for goods in goods_list:
        # 优先使用特定配置
        if goods.name in SPECIFIC_CONFIG:
            config = SPECIFIC_CONFIG[goods.name]
        # 使用分类默认值
        elif goods.category and goods.category.name in CATEGORY_DEFAULTS:
            config = CATEGORY_DEFAULTS[goods.category.name].copy()
            # 添加随机波动
            config['weight'] *= random.uniform(0.8, 1.2)
        else:
            # 默认值
            config = {'weight': 1.0, 'length': 25, 'width': 20, 'height': 15}
        
        goods.weight = round(config['weight'], 2)
        goods.length = config['length']
        goods.width = config['width']
        goods.height = config['height']
        goods.save()
        updated += 1
        print(f"✓ {goods.name[:25]}... | {goods.weight}kg | {goods.length}x{goods.width}x{goods.height}cm")
    
    print(f"\n完成！更新 {updated} 个商品的重量体积数据")

if __name__ == "__main__":
    run()
