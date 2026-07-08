import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()
from apps.goods.models import Goods

total = Goods.objects.count()
with_image = Goods.objects.exclude(image='').count()
without_image = Goods.objects.filter(image='').count()

print(f"总商品数: {total}")
print(f"有图片: {with_image}")
print(f"无图片: {without_image}")

if without_image > 0:
    print(f"\n删除无图片的商品:")
    for g in Goods.objects.filter(image=''):
        print(f"  - 删除: {g.name}")
        g.delete()
    print(f"已删除 {without_image} 个商品")

print(f"\n最终商品数: {Goods.objects.count()}")
