from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'goods', 'goods_name', 'goods_price', 'goods_image', 'quantity', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_text = serializers.CharField(read_only=True)
    delivery_status_text = serializers.CharField(source='get_delivery_status_display', read_only=True)
    rider_name = serializers.CharField(source='rider.real_name', read_only=True, default=None)

    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'total_amount', 'status', 'status_text',
            'receiver_name', 'receiver_phone', 'receiver_address', 'remark',
            'rider', 'rider_name', 'delivery_status', 'delivery_status_text',
            'assigned_at', 'delivered_at',
            'items', 'created_at', 'paid_at', 'shipped_at', 'completed_at'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    status_text = serializers.CharField(read_only=True)
    delivery_status_text = serializers.CharField(source='get_delivery_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_no', 'total_amount', 'status', 'status_text',
                  'delivery_status', 'delivery_status_text', 'created_at']


class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    remark = serializers.CharField(required=False, allow_blank=True)
