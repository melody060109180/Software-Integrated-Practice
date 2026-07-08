"""
防爆单功能模块
检查订单重量/体积是否超过骑手承载能力
"""

# 骑手交通工具配置
VEHICLE_CONFIG = {
    'bicycle': {
        'name': '自行车',
        'max_weight': 10,  # 最大承重(kg)
        'max_volume': 0.05,  # 最大体积(m³)
        'icon': 'bi-bicycle',
    },
    'motorcycle': {
        'name': '电动车',
        'max_weight': 30,  # 最大承重(kg)
        'max_volume': 0.15,  # 最大体积(m³)
        'icon': 'bi-ev-bike',
    },
    'car': {
        'name': '汽车',
        'max_weight': 100,  # 最大承重(kg)
        'max_volume': 1.0,  # 最大体积(m³)
        'icon': 'bi-car-front',
    },
}

# 默认电动车配置
DEFAULT_VEHICLE = 'motorcycle'


def get_order_weight(order):
    """计算订单总重量(kg)"""
    total_weight = 0
    for item in order.items.select_related('goods').all():
        if item.goods:
            total_weight += float(item.goods.weight) * item.quantity
    return round(total_weight, 2)


def get_order_volume(order):
    """计算订单总体积(m³)"""
    total_volume = 0
    for item in order.items.select_related('goods').all():
        if item.goods:
            total_volume += item.goods.volume * item.quantity
    return round(total_volume, 4)


def check_capacity(order, vehicle_type=None):
    """
    检查订单是否超过骑手承载能力
    返回: (is_safe, message, details)
    """
    if vehicle_type is None:
        vehicle_type = DEFAULT_VEHICLE
    
    config = VEHICLE_CONFIG.get(vehicle_type, VEHICLE_CONFIG[DEFAULT_VEHICLE])
    
    weight = get_order_weight(order)
    volume = get_order_volume(order)
    
    weight_ratio = weight / config['max_weight'] if config['max_weight'] > 0 else 0
    volume_ratio = volume / config['max_volume'] if config['max_volume'] > 0 else 0
    
    # 检查是否超载
    weight_overload = weight > config['max_weight']
    volume_overload = volume > config['max_volume']
    
    details = {
        'weight': weight,
        'volume': volume,
        'max_weight': config['max_weight'],
        'max_volume': config['max_volume'],
        'weight_ratio': round(weight_ratio * 100, 1),
        'volume_ratio': round(volume_ratio * 100, 1),
        'vehicle_name': config['name'],
        'vehicle_icon': config['icon'],
    }
    
    if weight_overload and volume_overload:
        return False, f'重量和体积均超载！需要{config["name"]}或更大运力', details
    elif weight_overload:
        return False, f'重量超载！当前{weight}kg，最大{config["max_weight"]}kg', details
    elif volume_overload:
        return False, f'体积超载！当前{volume:.4f}m³，最大{config["max_volume"]}m³', details
    else:
        # 检查是否接近满载
        if weight_ratio > 0.8 or volume_ratio > 0.8:
            return True, f'接近满载，请注意安全', details
        else:
            return True, f'正常载重', details


def get_suitable_vehicle(order):
    """推荐合适的交通工具"""
    weight = get_order_weight(order)
    volume = get_order_volume(order)
    
    for vehicle_type, config in VEHICLE_CONFIG.items():
        if weight <= config['max_weight'] and volume <= config['max_volume']:
            return vehicle_type, config
    
    # 如果都装不下，返回最大运力
    return 'car', VEHICLE_CONFIG['car']


def get_order_items_info(order):
    """获取订单商品的重量体积详情"""
    items_info = []
    for item in order.items.select_related('goods').all():
        if item.goods:
            item_weight = float(item.goods.weight) * item.quantity
            item_volume = item.goods.volume * item.quantity
            items_info.append({
                'goods_name': item.goods.name,
                'quantity': item.quantity,
                'unit_weight': item.goods.weight,
                'total_weight': round(item_weight, 2),
                'unit_volume': item.goods.volume,
                'total_volume': round(item_volume, 4),
            })
    return items_info
