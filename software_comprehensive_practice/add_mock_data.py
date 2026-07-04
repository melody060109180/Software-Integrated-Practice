import os
import sys
import django
import requests
from decimal import Decimal
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.files.base import ContentFile
from apps.goods.models import Category, Goods

# 商品数据：名称、描述、价格、库存、销量、分类名、图片URL
MOCK_PRODUCTS = [
    # 数码产品
    {"name": "iPhone 15 Pro Max 256GB", "desc": "苹果最新旗舰手机，A17 Pro芯片，钛金属设计", "price": 9999, "stock": 50, "sales": 1280, "cat": "电子产品", "img": "https://picsum.photos/seed/iphone15/400/400"},
    {"name": "MacBook Pro 14英寸 M3", "desc": "苹果笔记本电脑，M3芯片，16GB内存", "price": 14999, "stock": 30, "sales": 856, "cat": "电子产品", "img": "https://picsum.photos/seed/macbook/400/400"},
    {"name": "iPad Air 5 64GB", "desc": "苹果平板电脑，M1芯片，10.9英寸", "price": 4799, "stock": 80, "sales": 2340, "cat": "电子产品", "img": "https://picsum.photos/seed/ipad/400/400"},
    {"name": "AirPods Pro 2", "desc": "苹果无线耳机，主动降噪，USB-C充电", "price": 1799, "stock": 200, "sales": 5600, "cat": "电子产品", "img": "https://picsum.photos/seed/airpods/400/400"},
    {"name": "华为 Mate 60 Pro", "desc": "华为旗舰手机，麒麟9000S芯片，卫星通话", "price": 6999, "stock": 45, "sales": 3200, "cat": "电子产品", "img": "https://picsum.photos/seed/huawei/400/400"},
    {"name": "小米14 Ultra", "desc": "小米旗舰手机，骁龙8 Gen3，徕卡影像", "price": 5999, "stock": 60, "sales": 1890, "cat": "电子产品", "img": "https://picsum.photos/seed/xiaomi14/400/400"},
    {"name": "三星 Galaxy S24 Ultra", "desc": "三星旗舰手机，S Pen，AI功能", "price": 9699, "stock": 35, "sales": 980, "cat": "电子产品", "img": "https://picsum.photos/seed/samsung/400/400"},
    {"name": "索尼 WH-1000XM5", "desc": "索尼头戴式降噪耳机，30小时续航", "price": 2499, "stock": 100, "sales": 4200, "cat": "电子产品", "img": "https://picsum.photos/seed/sony/400/400"},

    # 数码产品
    {"name": "佳能 EOS R6 Mark II", "desc": "佳能全画幅微单相机，2420万像素", "price": 15999, "stock": 20, "sales": 320, "cat": "数码产品", "img": "https://picsum.photos/seed/canon/400/400"},
    {"name": "大疆 Mini 4 Pro", "desc": "大疆迷你无人机，4K HDR视频", "price": 4788, "stock": 40, "sales": 1560, "cat": "数码产品", "img": "https://picsum.photos/seed/dji/400/400"},
    {"name": "Switch OLED白色", "desc": "任天堂游戏机，7英寸OLED屏幕", "price": 2399, "stock": 70, "sales": 8900, "cat": "数码产品", "img": "https://picsum.photos/seed/switch/400/400"},
    {"name": "Kindle Paperwhite 5", "desc": "亚马逊电子书阅读器，6.8英寸", "price": 1068, "stock": 150, "sales": 3400, "cat": "数码产品", "img": "https://picsum.photos/seed/kindle/400/400"},
    {"name": "Apple Watch Series 9", "desc": "苹果智能手表，全天候显示屏", "price": 2999, "stock": 90, "sales": 2100, "cat": "数码产品", "img": "https://picsum.photos/seed/applewatch/400/400"},
    {"name": "华为 Watch GT 4", "desc": "华为智能手表，2周超长续航", "price": 1488, "stock": 120, "sales": 4500, "cat": "数码产品", "img": "https://picsum.photos/seed/huaweiwatch/400/400"},

    # 服装
    {"name": "男士纯棉短袖T恤", "desc": "100%纯棉，舒适透气，多色可选", "price": 79, "stock": 500, "sales": 12000, "cat": "服装", "img": "https://picsum.photos/seed/tshirt/400/400"},
    {"name": "女士碎花连衣裙", "desc": "法式复古碎花，收腰显瘦", "price": 199, "stock": 300, "sales": 8900, "cat": "服装", "img": "https://picsum.photos/seed/dress/400/400"},
    {"name": "男士牛仔裤直筒", "desc": "经典直筒版型，弹力面料", "price": 159, "stock": 400, "sales": 6700, "cat": "服装", "img": "https://picsum.photos/seed/jeans/400/400"},
    {"name": "女士运动卫衣", "desc": "加绒加厚，宽松版型", "price": 129, "stock": 350, "sales": 5400, "cat": "服装", "img": "https://picsum.photos/seed/hoodie/400/400"},
    {"name": "男士商务西装外套", "desc": "修身剪裁，商务休闲两穿", "price": 399, "stock": 150, "sales": 2300, "cat": "服装", "img": "https://picsum.photos/seed/suit/400/400"},
    {"name": "女士羽绒服轻薄款", "desc": "90%白鸭绒，轻便保暖", "price": 499, "stock": 200, "sales": 3800, "cat": "服装", "img": "https://picsum.photos/seed/jacket/400/400"},
    {"name": "男士polo衫翻领", "desc": "冰丝面料，速干透气", "price": 99, "stock": 450, "sales": 7600, "cat": "服装", "img": "https://picsum.photos/seed/polo/400/400"},
    {"name": "女士高腰阔腿裤", "desc": "显高显瘦，垂感面料", "price": 139, "stock": 280, "sales": 4100, "cat": "服装", "img": "https://picsum.photos/seed/pants/400/400"},

    # 生鲜果蔬
    {"name": "智利进口车厘子 2斤", "desc": "JJ级大果，新鲜直达", "price": 128, "stock": 100, "sales": 8900, "cat": "生鲜果蔬", "img": "https://picsum.photos/seed/cherry/400/400"},
    {"name": "新疆阿克苏苹果 5斤", "desc": "冰糖心苹果，脆甜多汁", "price": 39.9, "stock": 200, "sales": 15000, "cat": "生鲜果蔬", "img": "https://picsum.photos/seed/apple/400/400"},
    {"name": "泰国金枕头榴莲 3-4斤", "desc": "树上熟，软糯香甜", "price": 159, "stock": 80, "sales": 6700, "cat": "生鲜果蔬", "img": "https://picsum.photos/seed/durian/400/400"},
    {"name": "有机蔬菜礼盒 10种", "desc": "当季新鲜有机蔬菜", "price": 89, "stock": 150, "sales": 4500, "cat": "生鲜果蔬", "img": "https://picsum.photos/seed/veggie/400/400"},
    {"name": "海南三亚芒果 5斤", "desc": "大青芒，香甜无丝", "price": 49.9, "stock": 180, "sales": 11000, "cat": "生鲜果蔬", "img": "https://picsum.photos/seed/mango/400/400"},
    {"name": "澳洲安格斯牛排 2片装", "desc": "原切西冷，雪花纹理", "price": 199, "stock": 120, "sales": 5600, "cat": "生鲜果蔬", "img": "https://picsum.photos/seed/steak/400/400"},
    {"name": "三文鱼刺身 500g", "desc": "挪威进口，新鲜刺身级", "price": 168, "stock": 60, "sales": 3200, "cat": "生鲜果蔬", "img": "https://picsum.photos/seed/salmon/400/400"},
    {"name": "蓝莓 125g*4盒", "desc": "云南高原蓝莓，花青素丰富", "price": 59.9, "stock": 200, "sales": 9800, "cat": "生鲜果蔬", "img": "https://picsum.photos/seed/blueberry/400/400"},

    # 食品
    {"name": "良品铺子坚果大礼包 1.68kg", "desc": "10袋混合坚果，年货送礼", "price": 128, "stock": 300, "sales": 18000, "cat": "食品", "img": "https://picsum.photos/seed/nuts/400/400"},
    {"name": "蒙牛纯甄酸奶 200g*12", "desc": "原味酸奶，0添加", "price": 59.9, "stock": 500, "sales": 25000, "cat": "食品", "img": "https://picsum.photos/seed/yogurt/400/400"},
    {"name": "自嗨锅麻辣牛肉火锅", "desc": "自热火锅，15分钟即食", "price": 39.9, "stock": 400, "sales": 32000, "cat": "食品", "img": "https://picsum.photos/seed/hotpot/400/400"},
    {"name": "三只松鼠猪肉脯 200g", "desc": "靖江猪肉脯，蜜汁口味", "price": 29.9, "stock": 600, "sales": 28000, "cat": "食品", "img": "https://picsum.photos/seed/pork/400/400"},
    {"name": "农夫山泉天然水 550ml*24", "desc": "天然弱碱性水", "price": 39.9, "stock": 800, "sales": 45000, "cat": "食品", "img": "https://picsum.photos/seed/water/400/400"},
    {"name": "伊利金典纯牛奶 250ml*12", "desc": "有机纯牛奶，3.8g蛋白质", "price": 69.9, "stock": 350, "sales": 19000, "cat": "食品", "img": "https://picsum.photos/seed/milk/400/400"},
    {"name": "百草味麻花 500g", "desc": "天津小麻花，酥脆可口", "price": 19.9, "stock": 700, "sales": 16000, "cat": "食品", "img": "https://picsum.photos/seed/mahua/400/400"},
    {"name": "星巴克挂耳咖啡 10包", "desc": "精品深度烘焙，现磨风味", "price": 89, "stock": 250, "sales": 7800, "cat": "食品", "img": "https://picsum.photos/seed/coffee/400/400"},

    # 服装鞋帽
    {"name": "Nike Air Max 270", "desc": "耐克气垫跑鞋，缓震舒适", "price": 899, "stock": 100, "sales": 6700, "cat": "服装鞋帽", "img": "https://picsum.photos/seed/nike/400/400"},
    {"name": "Adidas Ultra Boost 22", "desc": "阿迪达斯boost跑鞋", "price": 1099, "stock": 80, "sales": 4500, "cat": "服装鞋帽", "img": "https://picsum.photos/seed/adidas/400/400"},
    {"name": "新百伦574经典款", "desc": "复古慢跑鞋，百搭款", "price": 599, "stock": 120, "sales": 8900, "cat": "服装鞋帽", "img": "https://picsum.photos/seed/newbalance/400/400"},
    {"name": "李宁篮球鞋韦德之道", "desc": "专业篮球鞋，碳板支撑", "price": 799, "stock": 60, "sales": 3200, "cat": "服装鞋帽", "img": "https://picsum.photos/seed/lining/400/400"},
    {"name": "Converse Chuck 70", "desc": "匡威1970s帆布鞋", "price": 499, "stock": 150, "sales": 12000, "cat": "服装鞋帽", "img": "https://picsum.photos/seed/converse/400/400"},
    {"name": "斐乐运动套装", "desc": "时尚运动套装，男女同款", "price": 699, "stock": 90, "sales": 3800, "cat": "服装鞋帽", "img": "https://picsum.photos/seed/fila/400/400"},
    {"name": "MLB棒球帽", "desc": "韩版潮流棒球帽", "price": 199, "stock": 200, "sales": 15000, "cat": "服装鞋帽", "img": "https://picsum.photos/seed/mlb/400/400"},
    {"name": "北面冲锋衣", "desc": "三合一冲锋衣，防水透气", "price": 1299, "stock": 70, "sales": 2900, "cat": "服装鞋帽", "img": "https://picsum.photos/seed/tnf/400/400"},

    # 家居日用
    {"name": "小米扫地机器人 X10+", "desc": "自动集尘，智能避障", "price": 2499, "stock": 50, "sales": 3400, "cat": "家居日用", "img": "https://picsum.photos/seed/robot/400/400"},
    {"name": "戴森V15吸尘器", "desc": "无线手持吸尘器，激光探测", "price": 4490, "stock": 30, "sales": 1800, "cat": "家居日用", "img": "https://picsum.photos/seed/dyson/400/400"},
    {"name": "九阳破壁机", "desc": "多功能料理机，静音设计", "price": 399, "stock": 100, "sales": 7600, "cat": "家居日用", "img": "https://picsum.photos/seed/blender/400/400"},
    {"name": "全棉四件套 1.8m", "desc": "60支长绒棉，亲肤透气", "price": 299, "stock": 150, "sales": 5400, "cat": "家居日用", "img": "https://picsum.photos/seed/bedding/400/400"},
    {"name": "智能门锁", "desc": "指纹密码锁，C级锁芯", "price": 999, "stock": 80, "sales": 4200, "cat": "家居日用", "img": "https://picsum.photos/seed/lock/400/400"},
    {"name": "空气净化器", "desc": "HEPA滤网，除甲醛", "price": 1299, "stock": 60, "sales": 3100, "cat": "家居日用", "img": "https://picsum.photos/seed/purifier/400/400"},
    {"name": "电饭煲 4L", "desc": "IH电磁加热，智能预约", "price": 499, "stock": 120, "sales": 6800, "cat": "家居日用", "img": "https://picsum.photos/seed/cooker/400/400"},
    {"name": "乳胶枕头", "desc": "泰国天然乳胶，护颈助眠", "price": 199, "stock": 200, "sales": 9200, "cat": "家居日用", "img": "https://picsum.photos/seed/pillow/400/400"},

    # 美妆护肤
    {"name": "兰蔻小黑瓶精华 50ml", "desc": "修护精华，淡化细纹", "price": 760, "stock": 80, "sales": 4500, "cat": "美妆护肤", "img": "https://picsum.photos/seed/lancome/400/400"},
    {"name": "雅诗兰黛眼霜 15ml", "desc": "小棕瓶眼霜，淡化黑眼圈", "price": 520, "stock": 100, "sales": 6700, "cat": "美妆护肤", "img": "https://picsum.photos/seed/estee/400/400"},
    {"name": "SK-II神仙水 230ml", "desc": "护肤精华露，焕亮肌肤", "price": 1190, "stock": 50, "sales": 3200, "cat": "美妆护肤", "img": "https://picsum.photos/seed/skii/400/400"},
    {"name": "MAC子弹头口红", "desc": "持久显色，丝绒质地", "price": 170, "stock": 200, "sales": 18000, "cat": "美妆护肤", "img": "https://picsum.photos/seed/mac/400/400"},
    {"name": "欧莱雅洗面奶 100ml", "desc": "氨基酸洁面，温和清洁", "price": 79, "stock": 300, "sales": 22000, "cat": "美妆护肤", "img": "https://picsum.photos/seed/loreal/400/400"},
    {"name": "资生堂防晒霜", "desc": "SPF50+，清爽不油腻", "price": 219, "stock": 150, "sales": 11000, "cat": "美妆护肤", "img": "https://picsum.photos/seed/shiseido/400/400"},
    {"name": "科颜氏面霜", "desc": "高保湿面霜，滋润不闷", "price": 295, "stock": 120, "sales": 7800, "cat": "美妆护肤", "img": "https://picsum.photos/seed/kiehls/400/400"},
    {"name": "迪奥真我香水 50ml", "desc": "经典花果香调", "price": 890, "stock": 40, "sales": 2100, "cat": "美妆护肤", "img": "https://picsum.photos/seed/dior/400/400"},

    # 食品饮料
    {"name": "元气森林气泡水 480ml*12", "desc": "0糖0脂0卡", "price": 59.9, "stock": 400, "sales": 35000, "cat": "食品饮料", "img": "https://picsum.photos/seed/genki/400/400"},
    {"name": "可口可乐 330ml*24罐", "desc": "经典配方，畅爽开怀", "price": 49.9, "stock": 600, "sales": 48000, "cat": "食品饮料", "img": "https://picsum.photos/seed/cola/400/400"},
    {"name": "三得利乌龙茶 500ml*15", "desc": "0糖乌龙茶，解腻清爽", "price": 59.9, "stock": 350, "sales": 22000, "cat": "食品饮料", "img": "https://picsum.photos/seed/tea/400/400"},
    {"name": "NFC鲜榨橙汁 300ml*6", "desc": "100%鲜榨，不加水不加糖", "price": 69.9, "stock": 200, "sales": 8900, "cat": "食品饮料", "img": "https://picsum.photos/seed/orange/400/400"},
    {"name": "农夫山泉东方树叶 500ml*12", "desc": "0糖茶饮料，多种口味", "price": 59.9, "stock": 300, "sales": 19000, "cat": "食品饮料", "img": "https://picsum.photos/seed/leaf/400/400"},
    {"name": "雀巢咖啡即饮 268ml*12", "desc": "醇品原味，提神醒脑", "price": 49.9, "stock": 500, "sales": 31000, "cat": "食品饮料", "img": "https://picsum.photos/seed/nescafe/400/400"},
    {"name": "王老吉凉茶 310ml*24罐", "desc": "怕上火喝王老吉", "price": 59.9, "stock": 400, "sales": 27000, "cat": "食品饮料", "img": "https://picsum.photos/seed/wlj/400/400"},
    {"name": "红牛维生素功能饮料 250ml*24", "desc": "补充能量，提神醒脑", "price": 108, "stock": 300, "sales": 15000, "cat": "食品饮料", "img": "https://picsum.photos/seed/redbull/400/400"},
]

def run():
    # 获取分类
    categories = {c.name: c for c in Category.objects.all()}
    
    created = 0
    for item in MOCK_PRODUCTS:
        cat_name = item["cat"]
        if cat_name not in categories:
            print(f"分类不存在: {cat_name}，跳过 {item['name']}")
            continue
        
        # 检查是否已存在同名商品
        if Goods.objects.filter(name=item["name"]).exists():
            continue
        
        goods = Goods(
            name=item["name"],
            description=item["desc"],
            price=Decimal(str(item["price"])),
            stock=item["stock"],
            sales=item["sales"],
            category=categories[cat_name],
            is_active=True,
        )
        
        # 下载图片
        try:
            resp = requests.get(item["img"], timeout=10)
            if resp.status_code == 200:
                img_name = item["img"].split("/")[-1].split("?")[0] + ".jpg"
                goods.image.save(img_name, ContentFile(resp.content), save=False)
        except Exception as e:
            print(f"下载图片失败: {item['name']} - {e}")
        
        goods.save()
        created += 1
        print(f"已创建: {item['name']} (¥{item['price']})")
    
    print(f"\n完成！共创建 {created} 个商品")

if __name__ == "__main__":
    run()
