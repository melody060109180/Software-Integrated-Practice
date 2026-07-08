"""
更新商品图片 - 使用可靠的图片服务
"""
import os
import sys
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.files.base import ContentFile
from apps.goods.models import Goods, Category

# 使用 picsum.photos 的固定种子图片（每个种子对应一张固定图片）
# 这样可以保证图片一致性
CATEGORY_IMAGES = {
    "电子产品": "https://picsum.photos/seed/electronics/400/400",
    "数码产品": "https://picsum.photos/seed/digital/400/400",
    "服装": "https://picsum.photos/seed/clothing/400/400",
    "生鲜果蔬": "https://picsum.photos/seed/fresh/400/400",
    "食品": "https://picsum.photos/seed/food/400/400",
    "服装鞋帽": "https://picsum.photos/seed/shoes/400/400",
    "家居日用": "https://picsum.photos/seed/home/400/400",
    "美妆护肤": "https://picsum.photos/seed/beauty/400/400",
    "食品饮料": "https://picsum.photos/seed/drinks/400/400",
}

def get_category_image(category_name):
    """获取分类对应的图片"""
    return CATEGORY_IMAGES.get(category_name, "https://picsum.photos/seed/default/400/400")

def run():
    """更新所有商品图片"""
    goods_list = Goods.objects.all()
    updated = 0
    
    for goods in goods_list:
        # 根据分类选择图片
        if goods.category:
            img_url = get_category_image(goods.category.name)
        else:
            img_url = "https://picsum.photos/seed/default/400/400"
        
        try:
            resp = requests.get(img_url, timeout=15)
            if resp.status_code == 200:
                # 保存图片
                img_name = f"{goods.id}_{goods.category.name if goods.category else 'default'}.jpg"
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
