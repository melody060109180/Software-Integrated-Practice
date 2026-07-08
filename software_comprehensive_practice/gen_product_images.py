"""为每个商品生成带名称的简洁商品占位图"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()
from apps.goods.models import Goods

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("需要安装 Pillow")
    exit(1)

# 商品配色方案
COLORS = {
    '食品饮料': ('#FF6B35', '#FFF3E0'),
    '食品': ('#E53935', '#FFEBEE'),
    '家居日用': ('#1E88E5', '#E3F2FD'),
    '生鲜果蔬': ('#43A047', '#E8F5E9'),
    '服装': ('#8E24AA', '#F3E5F5'),
}

def create_product_image(goods_name, category_name, save_path, width=400, height=400):
    bg_color = COLORS.get(category_name, ('#607D8B', '#ECEFF1'))[1]
    accent = COLORS.get(category_name, ('#607D8B', '#ECEFF1'))[0]

    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # 顶部色条
    draw.rectangle([0, 0, width, 6], fill=accent)

    # 商品名称（自动换行）
    try:
        font_large = ImageFont.truetype("msyh.ttc", 36)
        font_small = ImageFont.truetype("msyh.ttc", 20)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 简单换行
    lines = []
    line = ''
    for ch in goods_name:
        line += ch
        bbox = draw.textbbox((0, 0), line, font=font_large)
        if bbox[2] > width - 60:
            lines.append(line)
            line = ''
    if line:
        lines.append(line)

    y_start = (height - len(lines) * 45) // 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_large)
        x = (width - bbox[2]) // 2
        draw.text((x, y_start + i * 45), line, fill=accent, font=font_large)

    # 底部分类标签
    tag_text = f"【{category_name}】"
    bbox = draw.textbbox((0, 0), tag_text, font=font_small)
    tx = (width - bbox[2]) // 2
    draw.text((tx, height - 45), tag_text, fill='#999999', font=font_small)

    img.save(save_path, 'JPEG', quality=90)

media_dir = 'media/goods'
count = 0
for g in Goods.objects.select_related('category').all():
    filename = f'{g.id}_product.jpg'
    save_path = os.path.join(media_dir, filename)
    cat_name = g.category.name if g.category else '其他'

    create_product_image(g.name, cat_name, save_path)

    g.image.name = f'goods/{filename}'
    g.save(update_fields=['image'])
    count += 1
    print(f'  {g.id}. {g.name} -> {filename}')

print(f'\n完成: {count} 张商品图')
