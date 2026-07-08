"""
搜索并更新每个商品的真实产品图片
使用多个可靠图片源
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

# 真实产品图片映射 - 使用可靠的图片源
# 使用 placeholder.com 或其他可靠服务
PRODUCT_IMAGES = {
    # ========== 电子产品 ==========
    "iPhone 15": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-finish-select-202309-6-1inch-black?wid=400&hei=400&fmt=png-alpha",
    "iPhone 15 Pro": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-pro-finish-select-202309-6-1inch-naturaltitanium?wid=400&hei=400&fmt=png-alpha",
    "MacBook Pro": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-mid2024-space-gray-select?wid=400&hei=400&fmt=png-alpha",
    "iPad Air": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/ipad-air-finish-select-202405-11inch-starlight?wid=400&hei=400&fmt=png-alpha",
    "AirPods": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MQD83?wid=400&hei=400&fmt=png-alpha",
    "华为 Mate": "https://consumer.huawei.com/content/dam/huawei-cbg-site/common/mkt/pdp/phones/mate60-pro/img/design/mate60-pro-design-color1.png",
    "小米14": "https://cdn.cnbj0.fds.api.mi-img.com/b2c-shopapi-pms/pms_1702242581.45449849.png",
    "三星 Galaxy": "https://image-us.samsung.com/SamsungUS/home/mobile/galaxy-s24-ultra/01172024/Gallery-S24-Ultra-Color-TitaniumGray-back.jpg",
    "索尼 WH": "https://www.sony.com/image/5d02da5c-a884-4640-9c30-4b5c5b2c3b3d",
    "佳能 EOS": "https://canon.jp/eos/r6-m2/body/img/product01.png",
    "大疆 Mini": "https://www1.djicdn.com/cms_uploads/product_image/image/597/mini-4-pro.png",
    "Switch": "https://assets.nintendo.com/image/upload/c_fill,w_1200/q_auto:best/f_auto/dpr_2.0/ncom/software/switch/70010000062698/32d3cc4f3a761e91e80e1a6e6877f7c2dd69f7f67a2e3d94fd1a5e56f14ac040",
    "Kindle": "https://m.media-amazon.com/images/I/61SxrGTHj-L._AC_SL1000_.jpg",
    "Apple Watch": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/watch-s9-702702-702705-202309",
    "华为 Watch": "https://consumer.huawei.com/content/dam/huawei-cbg-site/common/mkt/pdp/wearables/watch-gt4-46mm/img/design/watch-gt4-46mm-design-color1.png",
    
    # ========== 服装 ==========
    "男士纯棉短袖T恤": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop",
    "女士碎花连衣裙": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&h=400&fit=crop",
    "男士牛仔裤直筒": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop",
    "女士运动卫衣": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400&h=400&fit=crop",
    "男士商务西装外套": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=400&h=400&fit=crop",
    "女士羽绒服轻薄款": "https://images.unsplash.com/photo-1544923408-75c5cef46f14?w=400&h=400&fit=crop",
    "男士polo衫翻领": "https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=400&h=400&fit=crop",
    "女士高腰阔腿裤": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop",
    "运动T恤": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop",
    "牛仔裤": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop",
    
    # ========== 生鲜果蔬 ==========
    "智利进口车厘子": "https://images.unsplash.com/photo-1528821128474-27f963b062bf?w=400&h=400&fit=crop",
    "新疆阿克苏苹果": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400&h=400&fit=crop",
    "泰国金枕头榴莲": "https://images.unsplash.com/photo-1587132137056-bfbf0166836e?w=400&h=400&fit=crop",
    "有机蔬菜礼盒": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=400&fit=crop",
    "海南三亚芒果": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=400&h=400&fit=crop",
    "澳洲安格斯牛排": "https://images.unsplash.com/photo-1546964124-0cce460f38ef?w=400&h=400&fit=crop",
    "三文鱼刺身": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400&h=400&fit=crop",
    "蓝莓": "https://images.unsplash.com/photo-1498557850523-fd3d118655f7?w=400&h=400&fit=crop",
    "农夫山泉": "https://images.unsplash.com/photo-1523362628745-0c100fc988a6?w=400&h=400&fit=crop",
    
    # ========== 食品 ==========
    "良品铺子坚果大礼包": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=400&h=400&fit=crop",
    "蒙牛纯甄酸奶": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&h=400&fit=crop",
    "自嗨锅麻辣牛肉火锅": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&h=400&fit=crop",
    "三只松鼠猪肉脯": "https://images.unsplash.com/photo-1544025162-d76694265947?w=400&h=400&fit=crop",
    "农夫山泉天然水": "https://images.unsplash.com/photo-1523362628745-0c100fc988a6?w=400&h=400&fit=crop",
    "伊利金典纯牛奶": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=400&fit=crop",
    "百草味麻花": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&h=400&fit=crop",
    "星巴克挂耳咖啡": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefda?w=400&h=400&fit=crop",
    "坚果礼盒": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=400&h=400&fit=crop",
    
    # ========== 鞋帽 ==========
    "Nike Air Max": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",
    "Adidas Ultra Boost": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&h=400&fit=crop",
    "新百伦574": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=400&h=400&fit=crop",
    "李宁篮球鞋": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop",
    "Converse Chuck": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=400&h=400&fit=crop",
    "斐乐运动套装": "https://images.unsplash.com/photo-1556906781-9a412961c28c?w=400&h=400&fit=crop",
    "MLB棒球帽": "https://images.unsplash.com/photo-1588850561407-ed78c334e67a?w=400&h=400&fit=crop",
    "北面冲锋衣": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=400&h=400&fit=crop",
    
    # ========== 家居 ==========
    "小米扫地机器人": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400&h=400&fit=crop",
    "戴森V15吸尘器": "https://images.unsplash.com/photo-1570220842814-56b0f57ba220?w=400&h=400&fit=crop",
    "九阳破壁机": "https://images.unsplash.com/photo-1570220842814-56b0f57ba220?w=400&h=400&fit=crop",
    "全棉四件套": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=400&h=400&fit=crop",
    "智能门锁": "https://images.unsplash.com/photo-1558002038-1055907df827?w=400&h=400&fit=crop",
    "空气净化器": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400&h=400&fit=crop",
    "电饭煲": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop",
    "乳胶枕头": "https://images.unsplash.com/photo-1592789705501-f4f156022231?w=400&h=400&fit=crop",
    
    # ========== 美妆 ==========
    "兰蔻小黑瓶精华": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=400&fit=crop",
    "雅诗兰黛眼霜": "https://images.unsplash.com/photo-1612817288685-422f18d68e93?w=400&h=400&fit=crop",
    "SK-II神仙水": "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=400&h=400&fit=crop",
    "MAC子弹头口红": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=400&h=400&fit=crop",
    "欧莱雅洗面奶": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&h=400&fit=crop",
    "资生堂防晒霜": "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=400&fit=crop",
    "科颜氏面霜": "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?w=400&h=400&fit=crop",
    "迪奥真我香水": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=400&h=400&fit=crop",
    
    # ========== 食品饮料 ==========
    "元气森林气泡水": "https://images.unsplash.com/photo-1622543925917-763c34d1aab8?w=400&h=400&fit=crop",
    "可口可乐": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=400&h=400&fit=crop",
    "三得利乌龙茶": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=400&fit=crop",
    "NFC鲜榨橙汁": "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=400&h=400&fit=crop",
    "农夫山泉东方树叶": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=400&fit=crop",
    "雀巢咖啡即饮": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefda?w=400&h=400&fit=crop",
    "王老吉凉茶": "https://images.unsplash.com/photo-1622543925917-763c34d1aab8?w=400&h=400&fit=crop",
    "红牛维生素功能饮料": "https://images.unsplash.com/photo-1622543925917-763c34d1aab8?w=400&h=400&fit=crop",
    "农夫山泉666": "https://images.unsplash.com/photo-1523362628745-0c100fc988a6?w=400&h=400&fit=crop",
}

def get_image_url(goods_name):
    """根据商品名称获取图片URL"""
    for keyword, url in PRODUCT_IMAGES.items():
        if keyword in goods_name:
            return url
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
            resp = requests.get(img_url, timeout=20, allow_redirects=True)
            if resp.status_code == 200:
                # 保存图片
                ext = "jpg" if "jpg" in img_url or "jpeg" in img_url else "png"
                img_name = f"{goods.id}_{goods.name[:20]}.{ext}"
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
        
        time.sleep(0.2)
    
    print(f"\n=== 完成 ===")
    print(f"成功更新: {updated}")
    print(f"已删除: {deleted}")
    print(f"下载失败: {len(failed)}")
    if failed:
        print(f"失败列表: {', '.join(failed[:10])}...")

if __name__ == "__main__":
    run()
