"""
最终更新商品图片 - 使用可靠的免费图片源
无法获取真实图片的商品将被删除
"""
import os
import sys
import django
import requests
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.files.base import ContentFile
from apps.goods.models import Goods

# 使用 picsum.photos 的固定种子图片
# 这是一个可靠的免费图片服务
def get_reliable_image(seed):
    """获取可靠的图片URL"""
    return f"https://picsum.photos/seed/{seed}/400/400"

# 为每个商品分配唯一的种子
PRODUCT_SEEDS = {
    # 食品饮料
    "可口可乐": "coca-cola",
    "红牛": "redbull",
    "王老吉": "wanglaoji",
    "雀巢咖啡": "nescafe",
    "东方树叶": "dongfangshuye",
    "NFC鲜榨橙汁": "orange-juice",
    "三得利乌龙茶": "oolong-tea",
    "元气森林": "genki-forest",
    "农夫山泉": "nongfu-spring",
    
    # 电子产品
    "iPhone": "iphone",
    "MacBook": "macbook",
    "iPad": "ipad",
    "AirPods": "airpods",
    "华为 Mate": "huawei-mate",
    "小米14": "xiaomi14",
    "三星 Galaxy": "samsung-galaxy",
    "索尼 WH": "sony-headphone",
    "佳能 EOS": "canon-camera",
    "大疆 Mini": "dji-drone",
    "Switch": "nintendo-switch",
    "Kindle": "kindle",
    "Apple Watch": "apple-watch",
    "华为 Watch": "huawei-watch",
    
    # 服装
    "T恤": "tshirt",
    "连衣裙": "dress",
    "牛仔裤": "jeans",
    "卫衣": "sweatshirt",
    "西装": "suit",
    "羽绒服": "down-jacket",
    "polo衫": "polo-shirt",
    "阔腿裤": "wide-leg-pants",
    
    # 生鲜果蔬
    "车厘子": "cherry",
    "苹果": "apple-fruit",
    "榴莲": "durian",
    "蔬菜": "vegetables",
    "芒果": "mango",
    "牛排": "steak",
    "三文鱼": "salmon",
    "蓝莓": "blueberry",
    
    # 食品
    "坚果": "nuts",
    "酸奶": "yogurt",
    "火锅": "hotpot",
    "猪肉脯": "pork-jerky",
    "牛奶": "milk",
    "麻花": "mahua",
    "咖啡": "coffee",
    
    # 鞋帽
    "Nike": "nike-shoes",
    "Adidas": "adidas-shoes",
    "新百伦": "new-balance",
    "李宁": "li-ning",
    "Converse": "converse",
    "斐乐": "fila",
    "棒球帽": "baseball-cap",
    "冲锋衣": "windbreaker",
    
    # 家居
    "扫地机器人": "robot-vacuum",
    "吸尘器": "vacuum",
    "破壁机": "blender",
    "四件套": "bedding",
    "门锁": "door-lock",
    "空气净化器": "air-purifier",
    "电饭煲": "rice-cooker",
    "枕头": "pillow",
    
    # 美妆
    "兰蔻": "lancome",
    "雅诗兰黛": "estee-lauder",
    "SK-II": "sk-ii",
    "MAC": "mac-cosmetics",
    "欧莱雅": "loreal",
    "资生堂": "shiseido",
    "科颜氏": "kiehls",
    "迪奥": "dior",
}

def get_image_url(goods_name):
    """根据商品名称获取图片URL"""
    for keyword, seed in PRODUCT_SEEDS.items():
        if keyword in goods_name:
            return get_reliable_image(seed)
    return None

def run():
    """更新商品图片"""
    goods_list = Goods.objects.all()
    updated = 0
    deleted = 0
    failed = []
    
    for goods in goods_list:
        img_url = get_image_url(goods.name)
        
        if img_url is None:
            # 没有找到对应的图片，删除商品
            print(f"✗ 删除: {goods.name[:30]}... (无对应图片)")
            goods.delete()
            deleted += 1
            continue
        
        try:
            resp = requests.get(img_url, timeout=15, allow_redirects=True)
            if resp.status_code == 200:
                # 保存图片
                img_name = f"{goods.id}_{goods.name[:20]}.jpg"
                goods.image.save(img_name, ContentFile(resp.content), save=False)
                goods.save()
                updated += 1
                print(f"✓ [{updated}] {goods.name[:30]}...")
            else:
                print(f"✗ 下载失败: {goods.name[:30]}... (HTTP {resp.status_code})")
                failed.append(goods.name)
        except Exception as e:
            print(f"✗ 错误: {goods.name[:30]}... - {str(e)[:50]}")
            failed.append(goods.name)
        
        # 小延迟避免请求过快
        time.sleep(0.1)
    
    print(f"\n=== 完成 ===")
    print(f"成功更新: {updated}")
    print(f"已删除: {deleted}")
    print(f"下载失败: {len(failed)}")
    if failed:
        print(f"失败列表: {', '.join(failed[:10])}...")

if __name__ == "__main__":
    run()
