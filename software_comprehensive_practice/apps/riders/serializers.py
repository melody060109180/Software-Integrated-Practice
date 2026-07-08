from rest_framework import serializers
from .models import Rider


class RiderSerializer(serializers.ModelSerializer):
    active_deliveries_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Rider
        fields = ['id', 'real_name', 'phone', 'id_number', 'is_available', 'is_active',
                  'active_deliveries_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
