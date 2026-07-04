from rest_framework import serializers
from .models import Category, Goods


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'icon', 'sort_order']


class GoodsSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Goods
        fields = [
            'id', 'name', 'description', 'price', 'stock', 
            'category', 'category_name', 'image', 'is_active', 
            'sales', 'average_rating', 'review_count',
            'created_at', 'updated_at'
        ]


class GoodsListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Goods
        fields = ['id', 'name', 'price', 'stock', 'category', 'category_name', 'image', 'sales', 'is_active']
