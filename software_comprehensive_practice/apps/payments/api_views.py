from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Payment
from .serializers import PaymentSerializer
from apps.orders.models import Order


@method_decorator(csrf_exempt, name='dispatch')
class PaymentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={'amount': order.total_amount}
        )
        return Response(PaymentSerializer(payment).data)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        payment = get_object_or_404(Payment, order=order)

        payment.status = 2
        payment.paid_at = timezone.now()
        payment.save()

        order.status = 2
        order.paid_at = timezone.now()
        order.save()

        return Response({'success': True, 'message': '支付成功'})


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCancelAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        return Response({'success': True, 'message': '支付已取消'})
