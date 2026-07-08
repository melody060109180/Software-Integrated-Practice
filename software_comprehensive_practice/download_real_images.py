"""逐个商品搜索真实产品图片并下载"""
import os, sys, django, urllib.request, ssl, time, re, hashlib, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()
from apps.goods.models import Goods

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url, referer='https://www.bing.com'):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': referer,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })
    return urllib.request.urlopen(req, timeout=20, context=ctx)

def bing_image_url(query):
    """从Bing图片搜索提取murl"""
    url = f'https://cn.bing.com/images/search?q={urllib.request.quote(query)}&qft=+filterui:imagesize-large&form=IRFLTR'
    try:
        html = fetch(url, 'https://cn.bing.com').read().decode('utf-8', errors='ignore')
        # 提取murl - Bing在murl字段存储原图URL
        matches = re.findall(r'murl&quot;:&quot;(https?://[^&]+?)&', html)
        for m in matches:
            if any(ext in m.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                if 'bing.com' not in m and 'microsoft' not in m:
                    return m
    except Exception as e:
        print(f'  Bing搜索异常: {e}')
    return None

def download(url, path):
    """下载图片"""
    try:
        data = fetch(url).read()
        if len(data) > 3000:  # 至少3KB
            with open(path, 'wb') as f:
                f.write(data)
            return True
    except Exception as e:
        print(f'  下载异常: {e}')
    return False

# 商品名 -> 搜索关键词（更精确）
products = [
    (82, '红牛维生素功能饮料250ml罐装整箱'),
    (81, '王老吉凉茶310ml罐装整箱'),
    (80, '雀巢丝滑拿铁即饮咖啡268ml'),
    (79, '农夫山泉东方树叶乌龙茶500ml'),
    (78, 'NFC鲜榨橙汁果汁'),
    (77, '三得利乌龙茶饮料500ml'),
    (76, '可口可乐330ml罐装整箱'),
    (75, '元气森林气泡水白桃味480ml'),
    (66, '天然乳胶枕头护颈'),
    (65, '美的电饭煲4L智能'),
    (64, '空气净化器家用除甲醛'),
    (63, '智能门锁指纹锁家用'),
    (62, '全棉四件套纯棉床单1.8m'),
    (61, '九阳破壁机家用料理机'),
    (60, '戴森V15无线吸尘器'),
    (59, '小米扫地机器人全自动'),
    (50, '星巴克挂耳咖啡精品速溶'),
    (49, '百草味麻花500g零食'),
    (48, '伊利金典纯牛奶250ml整箱'),
    (47, '农夫山泉天然矿泉水550ml整箱'),
    (46, '三只松鼠猪肉脯200g零食'),
    (45, '自嗨锅自热火锅麻辣牛肉'),
    (44, '蒙牛纯甄酸奶200g整箱'),
    (43, '良品铺子坚果大礼包零食'),
    (42, '新鲜蓝莓125g水果'),
    (39, '海南三亚芒果新鲜水果'),
    (38, '有机蔬菜礼盒新鲜蔬菜'),
    (37, '泰国金枕头榴莲新鲜水果'),
    (36, '新疆阿克苏苹果新鲜水果'),
    (35, '智利进口车厘子新鲜水果'),
    (11, '农夫山泉矿泉水瓶装'),
    (4, '男士牛仔裤直筒休闲'),
    (3, '运动T恤男短袖速干'),
]

media_dir = 'media/goods'
ok = 0
fail = 0

for gid, keyword in products:
    try:
        g = Goods.objects.get(id=gid)
    except Goods.DoesNotExist:
        continue

    print(f'[{gid}] {g.name} ... ', end='', flush=True)

    img_url = bing_image_url(keyword)
    if not img_url:
        print('未找到')
        fail += 1
        continue

    ext = '.jpg'
    if '.png' in img_url.lower():
        ext = '.png'
    filename = f'{gid}_real{ext}'
    save_path = os.path.join(media_dir, filename)

    if download(img_url, save_path):
        g.image.name = f'goods/{filename}'
        g.save(update_fields=['image'])
        print(f'OK ({os.path.getsize(save_path)//1024}KB)')
        ok += 1
    else:
        print('下载失败')
        fail += 1

    time.sleep(1.2)

print(f'\n完成: 成功{ok}, 失败{fail}')
