import os, sys, django, urllib.request, ssl, time, re, hashlib, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()
from apps.goods.models import Goods

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_url(url, referer='https://www.google.com'):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': referer,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    })
    return urllib.request.urlopen(req, timeout=20, context=ctx)

def google_image_search(query):
    """Google图片搜索，提取第一张产品图片"""
    url = f'https://www.google.com/search?q={urllib.request.quote(query)}&tbm=isch&safe=active'
    try:
        html = fetch_url(url).read().decode('utf-8', errors='ignore')
        # Google图片搜索结果中提取图片URL
        # 匹配 "https://...jpg" 或 "https://...png" 等
        patterns = [
            r'\["(https?://[^"]+\.(?:jpg|jpeg|png|webp)(?:\?[^"]*)?)"',
            r'ou":"(https?://[^"]+\.(?:jpg|jpeg|png|webp))',
        ]
        for pat in patterns:
            matches = re.findall(pat, html)
            # 过滤掉Google自己的图标和小图
            for m in matches:
                if 'google' not in m.lower() and 'gstatic' not in m.lower() and len(m) > 30:
                    return m
    except Exception as e:
        print(f'  Google搜索失败: {e}')
    return None

def download_img(url, save_path):
    try:
        data = fetch_url(url, referer='https://www.google.com').read()
        if len(data) > 2000:
            with open(save_path, 'wb') as f:
                f.write(data)
            return True
    except Exception as e:
        print(f'  下载失败: {e}')
    return False

# 商品列表：(id, 搜索关键词)
# 使用品牌名+产品类型，确保搜到正确的产品图
products = [
    (82, '红牛维生素功能饮料250ml'),
    (81, '王老吉凉茶310ml罐装'),
    (80, '雀巢即饮丝滑拿铁咖啡'),
    (79, '农夫山泉东方树叶乌龙茶'),
    (78, 'NFC鲜榨橙汁果汁'),
    (77, '三得利乌龙茶饮料'),
    (76, '可口可乐330ml罐装'),
    (75, '元气森林气泡水白桃味'),
    (66, '天然乳胶枕头'),
    (65, '美的电饭煲4L'),
    (64, '空气净化器家用'),
    (63, '智能门锁指纹锁'),
    (62, '全棉四件套纯棉床单'),
    (61, '九阳破壁机料理机'),
    (60, '戴森V15吸尘器'),
    (59, '小米扫地机器人'),
    (50, '星巴克挂耳咖啡'),
    (49, '百草味麻花零食'),
    (48, '伊利金典纯牛奶'),
    (47, '农夫山泉天然矿泉水'),
    (46, '三只松鼠猪肉脯'),
    (45, '自嗨锅自热火锅'),
    (44, '蒙牛纯甄酸奶'),
    (43, '良品铺子坚果大礼包'),
    (42, '蓝莓新鲜水果'),
    (39, '海南芒果新鲜'),
    (38, '有机蔬菜礼盒'),
    (37, '泰国金枕头榴莲'),
    (36, '新疆阿克苏苹果'),
    (35, '智利进口车厘子'),
    (11, '农夫山泉矿泉水瓶装'),
    (4, '男士牛仔裤直筒'),
    (3, '运动T恤男短袖'),
]

media_dir = 'media/goods'
success = 0
fail = 0

for gid, keyword in products:
    try:
        g = Goods.objects.get(id=gid)
    except Goods.DoesNotExist:
        continue

    print(f'[{gid}] {g.name}')

    img_url = google_image_search(keyword)
    if not img_url:
        print(f'  未找到图片')
        fail += 1
        continue

    ext = '.jpg'
    if '.png' in img_url.lower():
        ext = '.png'
    filename = f'{gid}_real{ext}'
    save_path = os.path.join(media_dir, filename)

    if download_img(img_url, save_path):
        g.image.name = f'goods/{filename}'
        g.save(update_fields=['image'])
        print(f'  OK -> {filename} ({os.path.getsize(save_path)//1024}KB)')
        success += 1
    else:
        print(f'  下载失败')
        fail += 1

    time.sleep(1)

print(f'\n完成: 成功{success}, 失败{fail}')
