import os, sys, django, urllib.request, ssl, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()
from apps.goods.models import Goods

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

import re, hashlib

def search_bing_image(query):
    url = f'https://www.bing.com/images/search?q={urllib.request.quote(query)}&form=HDRSC3&first=1'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')
        matches = re.findall(r'murl&quot;:&quot;(https?://[^&]+\.(?:jpg|jpeg|png|webp))', html, re.IGNORECASE)
        if matches:
            return matches[0]
    except Exception as e:
        print(f'  搜索失败: {e}')
    return None

def download_image(url, save_path):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.bing.com/'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        data = resp.read()
        if len(data) > 1000:
            with open(save_path, 'wb') as f:
                f.write(data)
            return True
    except Exception as e:
        print(f'  下载失败: {e}')
    return False

# 失败的商品，用更简单的关键词重试
retry_products = [
    (81, '王老吉凉茶'),
    (79, '东方树叶茶饮料'),
    (77, '三得利乌龙茶'),
    (65, '电饭煲'),
    (59, '小米扫地机器人'),
    (47, '农夫山泉矿泉水'),
    (39, '海南芒果'),
    (37, '榴莲'),
    (36, '阿克苏苹果'),
    (11, '农夫山泉'),
]

media_dir = 'media/goods'
success = 0

for gid, keyword in retry_products:
    try:
        g = Goods.objects.get(id=gid)
    except Goods.DoesNotExist:
        continue

    print(f'[{gid}] {g.name} - 重试: {keyword}')

    img_url = search_bing_image(keyword)
    if not img_url:
        print(f'  仍未找到图片')
        continue

    ext = '.jpg'
    if '.png' in img_url.lower():
        ext = '.png'
    filename = f'{gid}_{hashlib.md5(img_url.encode()).hexdigest()[:8]}{ext}'
    save_path = os.path.join(media_dir, filename)

    if download_image(img_url, save_path):
        g.image.name = f'goods/{filename}'
        g.save(update_fields=['image'])
        print(f'  OK -> {filename}')
        success += 1
    else:
        print(f'  下载失败')

    time.sleep(0.8)

print(f'\n重试完成: 成功{success}')
