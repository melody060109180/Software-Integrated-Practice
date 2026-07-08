"""
为每个商品分配唯一的图片
使用 picsum.photos 的固定种子
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

# 为每个商品ID分配唯一的种子图片
def get_unique_image(goods_id, goods_name):
    """获取唯一图片URL"""
    # 使用商品ID作为种子，确保每个商品都有唯一的图片
    return f"https://picsum.photos/seed/goods{goods_id}/400/400"

def run():
    """更新所有商品图片"""
    goods_list = Goods.objects.all()
    updated = 0
    failed = []
    
    for goods in goods_list:
        img_url = get_unique_image(goods.id, goods.name)
        
        try:
            resp = requests.get(img_url, timeout=20, allow_redirects=True)
            if resp.status_code == 200:
                # 保存图片
                img_name = f"{goods.id}_{goods.name[:20]}.jpg"
                goods.image.save(img_name, ContentFile(resp.content), save=False)
                goods.save()
                updated += 1
                print(f"✓ [{updated}/{len(goods_list)}] {goods.name[:30]}...")
            else:
                print(f"✗ 下载失败: {goods.name[:30]}... (HTTP {resp.status_code})")
                failed.append(goods.name)
        except Exception as e:
            print(f"✗ 错误: {goods.name[:30]}... - {str(e)[:50]}")
            failed.append(goods.name)
        
        time.sleep(0.1)
    
    print(f"\n=== 完成 ===")
    print(f"成功更新: {updated}")
    print(f"下载失败: {len(failed)}")
    if failed:
        print(f"失败列表: {', '.join(failed[:10])}...")

if __name__ == "__main__":
    run()
