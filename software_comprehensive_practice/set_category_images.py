"""
为每个分类的商品设置统一的分类图片
使用 placehold.co 服务生成分类图片
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

# 每个分类的图片颜色和标签
CATEGORY_CONFIG = {
    "电子产品": {"color": "007bff", "text": "Electronics"},
    "数码产品": {"color": "17a2b8", "text": "Digital"},
    "服装": {"color": "28a745", "text": "Clothing"},
    "生鲜果蔬": {"color": "dc3545", "text": "Fresh"},
    "食品": {"color": "fd7e14", "text": "Food"},
    "服装鞋帽": {"color": "6f42c1", "text": "Shoes"},
    "家居日用": {"color": "20c997", "text": "Home"},
    "美妆护肤": {"color": "e83e8c", "text": "Beauty"},
    "食品饮料": {"color": "ffc107", "text": "Drinks"},
}

def get_category_image(category_name):
    """获取分类图片URL"""
    config = CATEGORY_CONFIG.get(category_name, {"color": "6c757d", "text": "Product"})
    return f"https://placehold.co/400x400/{config['color']}/white?text={config['text']}"

def run():
    """更新所有商品图片"""
    goods_list = Goods.objects.all()
    updated = 0
    
    for goods in goods_list:
        # 根据分类选择图片
        if goods.category:
            img_url = get_category_image(goods.category.name)
        else:
            img_url = "https://placehold.co/400x400/6c757d/white?text=Product"
        
        try:
            resp = requests.get(img_url, timeout=10)
            if resp.status_code == 200:
                # 保存图片
                img_name = f"{goods.id}_{goods.category.name if goods.category else 'default'}.png"
                goods.image.save(img_name, ContentFile(resp.content), save=False)
                goods.save()
                updated += 1
                print(f"✓ [{updated}/{len(goods_list)}] {goods.name[:30]}...")
            else:
                print(f"✗ 下载失败: {goods.name[:30]}... (HTTP {resp.status_code})")
        except Exception as e:
            print(f"✗ 错误: {goods.name[:30]}... - {e}")
    
    print(f"\n完成！共更新 {updated}/{len(goods_list)} 个商品图片")

if __name__ == "__main__":
    run()
