from rest_framework import serializers
from .models import Merchant, MerchantGoods
from apps.goods.serializers import GoodsSerializer


class MerchantSerializer(serializers.ModelSerializer):
    total_goods = serializers.IntegerField(read_only=True)
    total_sales = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Merchant
        fields = [
            'id', 'shop_name', 'shop_logo', 'shop_description',
            'contact_phone', 'contact_email', 'address',
            'is_verified', 'is_active', 'total_goods', 'total_sales', 'total_revenue'
        ]


class MerchantGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(read_only=True)

    class Meta:
        model = MerchantGoods
        fields = ['id', 'goods', 'cost_price', 'is_featured', 'created_at']


class MerchantGoodsCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField(min_value=0)
    category = serializers.IntegerField()
    image = serializers.ImageField(required=False)
    cost_price = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_featured = serializers.BooleanField(default=False)


class MerchantDashboardSerializer(serializers.Serializer):
    total_goods = serializers.IntegerField()
    active_goods = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    month_orders = serializers.IntegerField()
    total_sales = serializers.IntegerField()
    month_sales = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    month_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
