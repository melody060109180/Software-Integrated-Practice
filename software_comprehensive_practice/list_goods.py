import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()
from apps.goods.models import Goods
for g in Goods.objects.all().order_by('id'):
    print(f"{g.id}|{g.name}|{g.category.name if g.category else '无分类'}")
