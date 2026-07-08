import os, sys, django, urllib.request, ssl, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()
from apps.goods.models import Goods

# 禁用SSL验证（部分图片源需要）
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 商品名 -> Bing图片搜索关键词 -> 预期图片URL（从Bing搜索结果提取）
# 我们用Bing搜索每个商品，提取第一张图片

import json, re, hashlib

def search_bing_image(query):
    """通过Bing搜索图片并返回第一个结果URL"""
    url = f'https://www.bing.com/images/search?q={urllib.request.quote(query)}&form=HDRSC3&first=1'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')
        # 提取图片URL - Bing在murl参数中存储原图链接
        matches = re.findall(r'murl&quot;:&quot;(https?://[^&]+\.(?:jpg|jpeg|png|webp))', html, re.IGNORECASE)
        if matches:
            return matches[0]
    except Exception as e:
        print(f'  搜索失败: {e}')
    return None

def download_image(url, save_path):
    """下载图片"""
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        data = resp.read()
        if len(data) > 1000:  # 至少1KB才算有效图片
            with open(save_path, 'wb') as f:
                f.write(data)
            return True
    except Exception as e:
        print(f'  下载失败: {e}')
    return False

# 所有商品的搜索关键词
products = [
    (82, '红牛维生素功能饮料250ml整箱'),
    (81, '王老吉凉茶310ml罐装'),
    (80, '雀巢即饮咖啡268ml'),
    (79, '农夫山泉东方树叶500ml'),
    (78, 'NFC鲜榨橙汁'),
    (77, '三得利乌龙茶500ml'),
    (76, '可口可乐330ml罐装整箱'),
    (75, '元气森林气泡水480ml'),
    (66, '乳胶枕头'),
    (65, '电饭煲4L'),
    (64, '空气净化器家用'),
    (63, '智能门锁'),
    (62, '全棉四件套床单'),
    (61, '九阳破壁机'),
    (60, '戴森吸尘器V15'),
    (59, '小米扫地机器人'),
    (50, '星巴克挂耳咖啡'),
    (49, '百草味麻花500g'),
    (48, '伊利金典纯牛奶250ml整箱'),
    (47, '农夫山泉天然水550ml整箱'),
    (46, '三只松鼠猪肉脯200g'),
    (45, '自嗨锅麻辣牛肉火锅'),
    (44, '蒙牛纯甄酸奶200g整箱'),
    (43, '良品铺子坚果大礼包'),
    (42, '蓝莓125g'),
    (39, '海南芒果5斤'),
    (38, '有机蔬菜礼盒'),
    (37, '泰国榴莲金枕头'),
    (36, '新疆阿克苏苹果5斤'),
    (35, '智利车厘子'),
    (11, '农夫山泉矿泉水'),
    (4, '牛仔裤男直筒'),
    (3, '运动T恤男'),
]

media_dir = 'media/goods'
success = 0
fail = 0

for gid, keyword in products:
    try:
        g = Goods.objects.get(id=gid)
    except Goods.DoesNotExist:
        print(f'[跳过] 商品{gid}不存在')
        continue

    print(f'[{gid}] {g.name} - 搜索: {keyword}')

    img_url = search_bing_image(keyword)
    if not img_url:
        print(f'  未找到图片')
        fail += 1
        continue

    # 生成文件名
    ext = '.jpg'
    if '.png' in img_url.lower():
        ext = '.png'
    filename = f'{gid}_{hashlib.md5(img_url.encode()).hexdigest()[:8]}{ext}'
    save_path = os.path.join(media_dir, filename)

    if download_image(img_url, save_path):
        # 更新数据库
        g.image.name = f'goods/{filename}'
        g.save(update_fields=['image'])
        print(f'  OK -> {filename}')
        success += 1
    else:
        print(f'  下载失败')
        fail += 1

    time.sleep(0.5)  # 避免请求过快

print(f'\n完成: 成功{success}, 失败{fail}')
