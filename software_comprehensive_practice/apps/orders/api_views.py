from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderListSerializer, CreateOrderSerializer
from apps.cart.models import Cart
from apps.users.models import Address


@method_decorator(csrf_exempt, name='dispatch')
class OrderListAPI(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


@method_decorator(csrf_exempt, name='dispatch')
class OrderDetailAPI(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class CreateOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_items = cart.items.select_related('goods').all()

            if not cart_items:
                return Response({'success': False, 'message': '购物车为空'}, status=status.HTTP_400_BAD_REQUEST)

            address_id = serializer.validated_data['address_id']
            address = get_object_or_404(Address, pk=address_id, user=request.user)

            order = Order.objects.create(
                user=request.user,
                total_amount=cart.total_price,
                receiver_name=address.name,
                receiver_phone=address.phone,
                receiver_address=address.full_address(),
                remark=serializer.validated_data.get('remark', ''),
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    goods=item.goods,
                    goods_name=item.goods.name,
                    goods_price=item.goods.price,
                    goods_image=item.goods.image.url if item.goods.image else '',
                    quantity=item.quantity,
                )
                item.goods.stock -= item.quantity
                item.goods.save()

            cart.items.all().delete()

            return Response({
                'success': True,
                'message': '订单创建成功',
                'order_id': order.pk,
                'order_no': order.order_no
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class CancelOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        if order.status == 1:
            order.status = 5
            order.save()
            for item in order.items.all():
                if item.goods:
                    item.goods.stock += item.quantity
                    item.goods.save()
            return Response({'success': True, 'message': '订单已取消'})
        return Response({'success': False, 'message': '该订单无法取消'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ConfirmOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        if order.status in [3, 4]:
            order.status = 4
            order.completed_at = timezone.now()
            order.save()
            return Response({'success': True, 'message': '已确认收货'})
        return Response({'success': False, 'message': '该订单无法确认收货'}, status=status.HTTP_400_BAD_REQUEST)
