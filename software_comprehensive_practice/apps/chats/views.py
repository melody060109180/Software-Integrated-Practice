from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
import json

from apps.orders.models import Order
from apps.merchants.models import Merchant
from apps.riders.models import Rider
from .models import ChatMessage


def _get_chat_type(user, other_user):
    """根据两个用户的角色确定对话类型"""
    user_is_merchant = hasattr(user, 'merchant')
    user_is_rider = hasattr(user, 'rider')
    other_is_merchant = hasattr(other_user, 'merchant')
    other_is_rider = hasattr(other_user, 'rider')

    if user_is_merchant or other_is_merchant:
        if user_is_rider or other_is_rider:
            return 'rider_merchant'
        else:
            return 'user_merchant'
    else:
        return 'user_rider'


def _find_merchant_user(order):
    """通过订单商品找到商家用户"""
    for item in order.items.all():
        if item.goods:
            # 方式1：通过 MerchantGoods 关联
            if hasattr(item.goods, 'merchant_goods'):
                return item.goods.merchant_goods.merchant.user
            # 方式2：通过商品创建者的 merchant 关联
            try:
                return item.goods.author.merchant.user
            except (AttributeError, Merchant.DoesNotExist):
                pass
    return None


def _check_order_permission(user, order):
    """检查用户是否有权访问该订单的聊天"""
    user_is_merchant = hasattr(user, 'merchant')
    user_is_rider = hasattr(user, 'rider')

    # 订单owner
    if order.user_id == user.id:
        return True
    # 商家：订单商品属于该商家
    if user_is_merchant:
        merchant_user = _find_merchant_user(order)
        if merchant_user and merchant_user.id == user.id:
            return True
    # 骑手：订单指派给了该骑手
    if user_is_rider:
        if order.rider and order.rider.user_id == user.id:
            return True
    return False


@login_required
def chat_page(request, order_id):
    """配送聊天页面"""
    order = get_object_or_404(Order, pk=order_id)
    user = request.user

    # 权限校验：只有订单相关方才能访问
    if not _check_order_permission(user, order):
        messages.error(request, '无权访问该订单的聊天')
        return redirect('orders:list')

    # 获取订单对应的商家和骑手
    merchant_user = _find_merchant_user(order)
    rider_user = order.rider.user if order.rider else None

    # 确定当前用户可以联系谁
    contacts = []
    user_is_merchant = hasattr(user, 'merchant')
    user_is_rider = hasattr(user, 'rider')
    user_is_customer = not user_is_merchant and not user_is_rider

    if user_is_customer:
        if merchant_user:
            contacts.append({
                'user_id': merchant_user.id,
                'name': merchant_user.merchant.shop_name,
                'role': '商家',
                'chat_type': 'user_merchant',
            })
        if rider_user:
            rider_name = rider_user.rider.real_name or rider_user.username
            contacts.append({
                'user_id': rider_user.id,
                'name': rider_name,
                'role': '骑手',
                'chat_type': 'user_rider',
            })
    elif user_is_merchant:
        contacts.append({
            'user_id': order.user.id,
            'name': order.receiver_name,
            'role': '用户',
            'chat_type': 'user_merchant',
        })
        if rider_user:
            rider_name = rider_user.rider.real_name or rider_user.username
            contacts.append({
                'user_id': rider_user.id,
                'name': rider_name,
                'role': '骑手',
                'chat_type': 'rider_merchant',
            })
    elif user_is_rider:
        contacts.append({
            'user_id': order.user.id,
            'name': order.receiver_name,
            'role': '用户',
            'chat_type': 'user_rider',
        })
        if merchant_user:
            contacts.append({
                'user_id': merchant_user.id,
                'name': merchant_user.merchant.shop_name,
                'role': '商家',
                'chat_type': 'rider_merchant',
            })

    can_chat = order.delivery_status in (1, 2)

    # 判断当前用户角色，用于面包屑
    user_role = 'customer'
    if user_is_merchant:
        user_role = 'merchant'
    elif user_is_rider:
        user_role = 'rider'

    context = {
        'order': order,
        'contacts': contacts,
        'can_chat': can_chat,
        'user_role': user_role,
    }
    return render(request, 'chats/chat.html', context)


@login_required
def chat_messages(request, order_id, user_id):
    """获取聊天消息"""
    order = get_object_or_404(Order, pk=order_id)
    other_user = get_object_or_404(User, pk=user_id)
    user = request.user

    # 权限校验
    if not _check_order_permission(user, order):
        return JsonResponse({'error': '无权访问'}, status=403)

    chat_type = _get_chat_type(user, other_user)

    msgs = ChatMessage.objects.filter(
        order=order,
        chat_type=chat_type,
    ).filter(
        Q(sender=user, receiver=other_user) | Q(sender=other_user, receiver=user)
    )

    msgs.filter(receiver=user, is_read=False).update(is_read=True)

    data = []
    for msg in msgs:
        data.append({
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.first_name or msg.sender.username,
            'message': msg.message,
            'created_at': msg.created_at.strftime('%m-%d %H:%M'),
            'is_mine': msg.sender == user,
        })

    return JsonResponse({'messages': data})


@login_required
def chat_send(request):
    """发送聊天消息"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)

    order_id = data.get('order_id')
    receiver_id = data.get('receiver_id')
    message = data.get('message', '').strip()
    chat_type = data.get('chat_type', '')

    if not order_id or not receiver_id or not message:
        return JsonResponse({'error': '缺少必要参数'}, status=400)

    order = get_object_or_404(Order, pk=order_id)
    receiver = get_object_or_404(User, pk=receiver_id)

    # 权限校验：发送者必须与订单相关
    if not _check_order_permission(request.user, order):
        return JsonResponse({'error': '无权发送消息'}, status=403)

    # 配送完成后禁止发送
    if order.delivery_status not in (1, 2):
        return JsonResponse({'error': '配送已完成，无法发送消息'}, status=400)

    # 验证 chat_type 与实际角色一致
    actual_chat_type = _get_chat_type(request.user, receiver)
    if chat_type and chat_type != actual_chat_type:
        chat_type = actual_chat_type

    ChatMessage.objects.create(
        order=order,
        sender=request.user,
        receiver=receiver,
        chat_type=chat_type,
        message=message,
    )

    return JsonResponse({'status': 'ok'})
