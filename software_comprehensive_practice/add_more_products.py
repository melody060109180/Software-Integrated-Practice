"""添加更多仓库式生活用品商品"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()
from apps.goods.models import Goods, Category
from decimal import Decimal

# 获取分类
cat_food = Category.objects.get(id=3)       # 食品
cat_drink = Category.objects.get(id=9)      # 食品饮料
cat_home = Category.objects.get(id=7)       # 家居日用
cat_fresh = Category.objects.get(id=5)      # 生鲜果蔬
cat_cloth = Category.objects.get(id=2)      # 服装

new_products = [
    # 食品
    {'name': '康师傅红烧牛肉面 5包', 'price': 12.90, 'stock': 500, 'category': cat_food},
    {'name': '乐事薯片原味 104g', 'price': 9.90, 'stock': 800, 'category': cat_food},
    {'name': '奥利奥饼干夹心 97g', 'price': 7.90, 'stock': 600, 'category': cat_food},
    {'name': '旺仔小馒头 230g', 'price': 12.80, 'stock': 400, 'category': cat_food},
    {'name': '上好佳虾片 50g', 'price': 5.90, 'stock': 700, 'category': cat_food},
    {'name': '德芙巧克力丝滑牛奶 43g', 'price': 12.90, 'stock': 500, 'category': cat_food},
    {'name': '王饱饱麦片水果坚果 400g', 'price': 39.90, 'stock': 300, 'category': cat_food},
    {'name': '汤达人豚骨拉面 5包', 'price': 29.90, 'stock': 400, 'category': cat_food},
    {'name': '海苔小零食即食 25g', 'price': 12.90, 'stock': 600, 'category': cat_food},
    {'name': '旺旺仙贝大礼包 520g', 'price': 19.90, 'stock': 350, 'category': cat_food},

    # 食品饮料
    {'name': '脉动维生素饮料 600ml', 'price': 4.50, 'stock': 1000, 'category': cat_drink},
    {'name': '维他柠檬茶 250ml*24', 'price': 39.90, 'stock': 300, 'category': cat_drink},
    {'name': '伊利安慕希酸奶 205g*12', 'price': 59.90, 'stock': 250, 'category': cat_drink},
    {'name': '怡宝纯净水 555ml*24', 'price': 28.00, 'stock': 600, 'category': cat_drink},
    {'name': '美汁源果粒橙 420ml*12', 'price': 39.90, 'stock': 350, 'category': cat_drink},
    {'name': '百岁山矿泉水 570ml*24', 'price': 36.00, 'stock': 400, 'category': cat_drink},
    {'name': '元气森林燃茶 480ml*12', 'price': 59.90, 'stock': 300, 'category': cat_drink},
    {'name': '味全每日C果汁 300ml*12', 'price': 59.90, 'stock': 250, 'category': cat_drink},

    # 家居日用
    {'name': '蓝月亮洗衣液 3kg', 'price': 39.90, 'stock': 500, 'category': cat_home},
    {'name': '维达抽纸 3层130抽*24包', 'price': 49.90, 'stock': 400, 'category': cat_home},
    {'name': '舒肤佳沐浴露 720ml', 'price': 29.90, 'stock': 600, 'category': cat_home},
    {'name': '格力电风扇落地扇', 'price': 199.00, 'stock': 100, 'category': cat_home},
    {'name': '苏泊尔炒锅 32cm', 'price': 129.00, 'stock': 200, 'category': cat_home},
    {'name': '威猛先生厨房清洁剂 500ml', 'price': 15.90, 'stock': 800, 'category': cat_home},
    {'name': '心相印湿巾 80片*5包', 'price': 19.90, 'stock': 500, 'category': cat_home},
    {'name': '飞利浦电动牙刷 HX6730', 'price': 299.00, 'stock': 150, 'category': cat_home},
    {'name': '美的电热水壶 1.7L', 'price': 79.00, 'stock': 300, 'category': cat_home},
    {'name': '南极人毛巾纯棉 3条装', 'price': 29.90, 'stock': 600, 'category': cat_home},

    # 生鲜果蔬
    {'name': '广西百香果 10个装', 'price': 29.90, 'stock': 400, 'category': cat_fresh},
    {'name': '山东大樱桃 1kg', 'price': 59.90, 'stock': 300, 'category': cat_fresh},
    {'name': '福建琯溪蜜柚 2个', 'price': 29.90, 'stock': 350, 'category': cat_fresh},
    {'name': '云南红心火龙果 3斤', 'price': 39.90, 'stock': 300, 'category': cat_fresh},
    {'name': '四川猕猴桃 12个', 'price': 39.90, 'stock': 250, 'category': cat_fresh},
    {'name': '有机西兰花 500g', 'price': 12.90, 'stock': 400, 'category': cat_fresh},
    {'name': '精品胡萝卜 1kg', 'price': 8.90, 'stock': 500, 'category': cat_fresh},
    {'name': '新鲜玉米 6根装', 'price': 19.90, 'stock': 350, 'category': cat_fresh},

    # 服装
    {'name': '男士纯棉背心 3件装', 'price': 49.90, 'stock': 400, 'category': cat_cloth},
    {'name': '女士纯棉袜子 5双装', 'price': 19.90, 'stock': 600, 'category': cat_cloth},
    {'name': '男士休闲短裤', 'price': 69.00, 'stock': 300, 'category': cat_cloth},
    {'name': '儿童纯棉T恤', 'price': 39.90, 'stock': 350, 'category': cat_cloth},
]

created = 0
for p in new_products:
    goods = Goods.objects.create(
        name=p['name'],
        price=p['price'],
        stock=p['stock'],
        category=p['category'],
        description=p['name'],
        weight=0.5,
        length=20,
        width=15,
        height=10,
    )
    created += 1
    print(f'  + {goods.id}. {goods.name} - ¥{goods.price}')

print(f'\n新增 {created} 件商品，总计 {Goods.objects.count()} 件')
