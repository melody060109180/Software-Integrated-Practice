from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    rating_stars = serializers.CharField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'username', 'goods', 'rating', 'rating_stars', 'content', 'created_at']


class CreateReviewSerializer(serializers.Serializer):
    goods_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    content = serializers.CharField(required=False, allow_blank=True)
