from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    status_text = serializers.CharField(read_only=True)
    method_text = serializers.CharField(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'payment_no', 'amount', 'method', 'method_text', 'status', 'status_text', 'paid_at']
