"""
最终清理：删除无法获取真实图片的商品
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()
from apps.goods.models import Goods

# 检查每个商品的图片文件是否存在且有效
total = Goods.objects.count()
valid = 0
invalid = 0

print("=== 检查商品图片 ===")
for g in Goods.objects.all():
    if g.image and os.path.exists(g.image.path):
        valid += 1
    else:
        print(f"✗ 无效图片: {g.name} (ID:{g.id})")
        invalid += 1

print(f"\n总商品数: {total}")
print(f"有效图片: {valid}")
print(f"无效图片: {invalid}")

if invalid > 0:
    print(f"\n删除无效图片的商品:")
    for g in Goods.objects.all():
        if not g.image or not os.path.exists(g.image.path):
            print(f"  - 删除: {g.name}")
            g.delete()
    print(f"已删除 {invalid} 个商品")

final_count = Goods.objects.count()
print(f"\n最终商品数: {final_count}")

# 显示剩余商品
print("\n=== 剩余商品列表 ===")
for g in Goods.objects.all().order_by('id'):
    print(f"{g.id}|{g.name}|{g.category.name if g.category else '无分类'}")
