from rest_framework import serializers
from .models import Cart, CartItem
from apps.goods.serializers import GoodsListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    goods = GoodsListSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'goods', 'quantity', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_quantity', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    goods_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
