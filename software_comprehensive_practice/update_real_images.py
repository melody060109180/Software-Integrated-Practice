"""
更新商品图片为真实图片
使用免费图片服务获取真实商品图片
"""
import os
import sys
import django
import requests
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.files.base import ContentFile
from apps.goods.models import Goods

# 真实商品图片映射 (商品名称关键词 -> 图片URL)
# 使用 Unsplash Source 或其他免费图片服务
REAL_IMAGES = {
    # 电子产品
    "iPhone": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop",
    "MacBook": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop",
    "iPad": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop",
    "AirPods": "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=400&h=400&fit=crop",
    "华为": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400&h=400&fit=crop",
    "小米": "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=400&h=400&fit=crop",
    "三星": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&h=400&fit=crop",
    "索尼": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
    "佳能": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400&h=400&fit=crop",
    "大疆": "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=400&h=400&fit=crop",
    "Switch": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=400&h=400&fit=crop",
    "Kindle": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&h=400&fit=crop",
    "Apple Watch": "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400&h=400&fit=crop",
    "华为 Watch": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop",
    
    # 服装
    "T恤": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop",
    "连衣裙": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&h=400&fit=crop",
    "牛仔裤": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop",
    "卫衣": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400&h=400&fit=crop",
    "西装": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=400&h=400&fit=crop",
    "羽绒服": "https://images.unsplash.com/photo-1544923408-75c5cef46f14?w=400&h=400&fit=crop",
    "polo衫": "https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=400&h=400&fit=crop",
    "阔腿裤": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop",
    
    # 生鲜果蔬
    "车厘子": "https://images.unsplash.com/photo-1528821128474-27f963b062bf?w=400&h=400&fit=crop",
    "苹果": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400&h=400&fit=crop",
    "榴莲": "https://images.unsplash.com/photo-1587132137056-bfbf0166836e?w=400&h=400&fit=crop",
    "蔬菜": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=400&fit=crop",
    "芒果": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=400&h=400&fit=crop",
    "牛排": "https://images.unsplash.com/photo-1546964124-0cce460f38ef?w=400&h=400&fit=crop",
    "三文鱼": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400&h=400&fit=crop",
    "蓝莓": "https://images.unsplash.com/photo-1498557850523-fd3d118655f7?w=400&h=400&fit=crop",
    
    # 食品
    "坚果": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=400&h=400&fit=crop",
    "酸奶": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&h=400&fit=crop",
    "火锅": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&h=400&fit=crop",
    "猪肉脯": "https://images.unsplash.com/photo-1544025162-d76694265947?w=400&h=400&fit=crop",
    "农夫山泉": "https://images.unsplash.com/photo-1523362628745-0c100fc988a6?w=400&h=400&fit=crop",
    "牛奶": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=400&fit=crop",
    "麻花": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&h=400&fit=crop",
    "咖啡": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefda?w=400&h=400&fit=crop",
    
    # 鞋帽
    "Nike": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",
    "Adidas": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&h=400&fit=crop",
    "新百伦": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=400&h=400&fit=crop",
    "李宁": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop",
    "Converse": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=400&h=400&fit=crop",
    "斐乐": "https://images.unsplash.com/photo-1556906781-9a412961c28c?w=400&h=400&fit=crop",
    "棒球帽": "https://images.unsplash.com/photo-1588850561407-ed78c334e67a?w=400&h=400&fit=crop",
    "冲锋衣": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=400&h=400&fit=crop",
    
    # 家居
    "扫地机器人": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400&h=400&fit=crop",
    "吸尘器": "https://images.unsplash.com/photo-1570220842814-56b0f57ba220?w=400&h=400&fit=crop",
    "破壁机": "https://images.unsplash.com/photo-1570220842814-56b0f57ba220?w=400&h=400&fit=crop",
    "四件套": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=400&h=400&fit=crop",
    "门锁": "https://images.unsplash.com/photo-1558002038-1055907df827?w=400&h=400&fit=crop",
    "空气净化器": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400&h=400&fit=crop",
    "电饭煲": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop",
    "枕头": "https://images.unsplash.com/photo-1592789705501-f4f156022231?w=400&h=400&fit=crop",
    
    # 美妆
    "兰蔻": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=400&fit=crop",
    "雅诗兰黛": "https://images.unsplash.com/photo-1612817288685-422f18d68e93?w=400&h=400&fit=crop",
    "SK-II": "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=400&h=400&fit=crop",
    "MAC": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=400&h=400&fit=crop",
    "欧莱雅": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&h=400&fit=crop",
    "资生堂": "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=400&fit=crop",
    "科颜氏": "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?w=400&h=400&fit=crop",
    "迪奥": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=400&h=400&fit=crop",
    
    # 饮料
    "元气森林": "https://images.unsplash.com/photo-1622543925917-763c34d1aab8?w=400&h=400&fit=crop",
    "可口可乐": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=400&h=400&fit=crop",
    "乌龙茶": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=400&fit=crop",
    "橙汁": "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=400&h=400&fit=crop",
    "东方树叶": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=400&fit=crop",
    "雀巢咖啡": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefda?w=400&h=400&fit=crop",
    "王老吉": "https://images.unsplash.com/photo-1622543925917-763c34d1aab8?w=400&h=400&fit=crop",
    "红牛": "https://images.unsplash.com/photo-1622543925917-763c34d1aab8?w=400&h=400&fit=crop",
}

# 默认图片（如果找不到匹配的）
DEFAULT_IMAGE = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop"

def get_image_url(goods_name):
    """根据商品名称获取图片URL"""
    for keyword, url in REAL_IMAGES.items():
        if keyword in goods_name:
            return url
    return DEFAULT_IMAGE

def run():
    """更新所有商品图片"""
    goods_list = Goods.objects.all()
    updated = 0
    
    for goods in goods_list:
        img_url = get_image_url(goods.name)
        
        try:
            resp = requests.get(img_url, timeout=15)
            if resp.status_code == 200:
                # 保存图片
                img_name = f"{goods.id}_{goods.name[:20]}.jpg"
                goods.image.save(img_name, ContentFile(resp.content), save=False)
                goods.save()
                updated += 1
                print(f"✓ 已更新: {goods.name[:30]}...")
            else:
                print(f"✗ 下载失败: {goods.name[:30]}... (HTTP {resp.status_code})")
        except Exception as e:
            print(f"✗ 错误: {goods.name[:30]}... - {e}")
    
    print(f"\n完成！共更新 {updated}/{len(goods_list)} 个商品图片")

if __name__ == "__main__":
    run()
