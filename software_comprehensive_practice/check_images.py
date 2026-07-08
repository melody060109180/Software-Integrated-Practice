import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()

from apps.goods.models import Goods

print("=== 商品图片检查 ===")
for g in Goods.objects.all()[:10]:
    img_url = g.image.url if g.image else "No image"
    print(f"{g.id}: {g.name[:30]}... - {img_url}")

print("\n=== 图片文件存在性检查 ===")
goods_with_images = Goods.objects.filter(image__isnull=False)[:5]
for g in goods_with_images:
    if g.image:
        full_path = g.image.path
        exists = os.path.exists(full_path)
        print(f"{g.id}: {g.image.name} - 存在: {exists}")
