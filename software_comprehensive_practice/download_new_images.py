"""为新增商品下载真实产品图片"""
import os, sys, django, urllib.request, ssl, time, re, hashlib
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()
from apps.goods.models import Goods

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url, referer='https://cn.bing.com'):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': referer,
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })
    return urllib.request.urlopen(req, timeout=20, context=ctx)

def bing_url(q):
    url = f'https://cn.bing.com/images/search?q={urllib.request.quote(q)}&qft=+filterui:imagesize-large&form=IRFLTR'
    html = fetch(url).read().decode('utf-8', errors='ignore')
    for m in re.findall(r'murl&quot;:&quot;(https?://[^&]+?)&', html):
        if any(x in m.lower() for x in ['.jpg', '.jpeg', '.png']):
            if 'bing.com' not in m and 'microsoft' not in m:
                return m
    return None

def dl(url, path):
    data = fetch(url).read()
    if len(data) > 3000:
        with open(path, 'wb') as f:
            f.write(data)
        return True
    return False

# 新增商品的搜索关键词
products = [
    (84, '康师傅红烧牛肉面方便面'),
    (85, '乐事薯片原味'),
    (86, '奥利奥饼干'),
    (87, '旺仔小馒头'),
    (88, '上好佳虾片'),
    (89, '德芙巧克力'),
    (90, '王饱饱麦片'),
    (91, '汤达人豚骨拉面'),
    (92, '海苔零食即食'),
    (93, '旺旺仙贝大礼包'),
    (94, '脉动维生素饮料'),
    (95, '维他柠檬茶'),
    (96, '伊利安慕希酸奶'),
    (97, '怡宝纯净水'),
    (98, '美汁源果粒橙'),
    (99, '百岁山矿泉水'),
    (100, '元气森林燃茶'),
    (101, '味全每日C果汁'),
    (102, '蓝月亮洗衣液'),
    (103, '维达抽纸'),
    (104, '舒肤佳沐浴露'),
    (105, '格力电风扇'),
    (106, '苏泊尔炒锅'),
    (107, '威猛先生厨房清洁剂'),
    (108, '心相印湿巾'),
    (109, '飞利浦电动牙刷'),
    (110, '美的电热水壶'),
    (111, '南极人毛巾'),
    (112, '百香果新鲜水果'),
    (113, '山东大樱桃'),
    (114, '琯溪蜜柚'),
    (115, '红心火龙果'),
    (116, '四川猕猴桃'),
    (117, '有机西兰花'),
    (118, '精品胡萝卜'),
    (119, '新鲜玉米'),
    (120, '男士纯棉背心'),
    (121, '女士纯棉袜子'),
    (122, '男士休闲短裤'),
    (123, '儿童纯棉T恤'),
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

    img_url = bing_url(keyword)
    if not img_url:
        print('未找到')
        fail += 1
        continue

    ext = '.png' if '.png' in img_url.lower() else '.jpg'
    filename = f'{gid}_real{ext}'
    save_path = os.path.join(media_dir, filename)

    try:
        if dl(img_url, save_path):
            g.image.name = f'goods/{filename}'
            g.save(update_fields=['image'])
            print(f'OK ({os.path.getsize(save_path)//1024}KB)')
            ok += 1
        else:
            print('下载失败')
            fail += 1
    except Exception as e:
        print(f'异常: {e}')
        fail += 1

    time.sleep(1)

print(f'\n完成: 成功{ok}, 失败{fail}')
