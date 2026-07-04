from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, F
from .models import Merchant, MerchantGoods
from .serializers import (
    MerchantSerializer, MerchantGoodsSerializer,
    MerchantGoodsCreateSerializer, MerchantDashboardSerializer
)
from apps.goods.models import Goods, Category
from apps.orders.models import Order, OrderItem


@method_decorator(csrf_exempt, name='dispatch')
class MerchantRegisterAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth.models import User
        from django.contrib.auth import login

        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        shop_name = request.data.get('shop_name')
        contact_phone = request.data.get('contact_phone')
        address = request.data.get('address')

        if User.objects.filter(username=username).exists():
            return Response({'success': False, 'message': '用户名已存在'}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        merchant = Merchant.objects.create(
            user=user, shop_name=shop_name,
            contact_phone=contact_phone, address=address
        )
        login(request, user)

        return Response({
            'success': True, 'message': '商家注册成功',
            'merchant': MerchantSerializer(merchant).data
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class MerchantDashboardAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        merchant = get_object_or_404(Merchant, user=request.user)
        today = timezone.now().date()
        month_start = today.replace(day=1)
        merchant_goods_ids = merchant.goods.values_list('goods_id', flat=True)

        total_goods = merchant.goods.count()
        active_goods = merchant.goods.filter(goods__is_active=True).count()
        total_orders = Order.objects.filter(items__goods_id__in=merchant_goods_ids).distinct().count()
        month_orders = Order.objects.filter(
            items__goods_id__in=merchant_goods_ids, created_at__date__gte=month_start
        ).distinct().count()
        total_sales = OrderItem.objects.filter(
            goods_id__in=merchant_goods_ids, order__status__in=[2, 3, 4]
        ).aggregate(total=Sum('quantity'))['total'] or 0
        month_sales = OrderItem.objects.filter(
            goods_id__in=merchant_goods_ids, order__status__in=[2, 3, 4],
            order__created_at__date__gte=month_start
        ).aggregate(total=Sum('quantity'))['total'] or 0
        total_revenue = OrderItem.objects.filter(
            goods_id__in=merchant_goods_ids, order__status__in=[2, 3, 4]
        ).aggregate(total=Sum(F('goods_price') * F('quantity')))['total'] or 0
        month_revenue = OrderItem.objects.filter(
            goods_id__in=merchant_goods_ids, order__status__in=[2, 3, 4],
            order__created_at__date__gte=month_start
        ).aggregate(total=Sum(F('goods_price') * F('quantity')))['total'] or 0

        return Response({
            'shop_name': merchant.shop_name,
            'total_goods': total_goods, 'active_goods': active_goods,
            'total_orders': total_orders, 'month_orders': month_orders,
            'total_sales': total_sales, 'month_sales': month_sales,
            'total_revenue': total_revenue, 'month_revenue': month_revenue,
        })


@method_decorator(csrf_exempt, name='dispatch')
class MerchantGoodsListAPI(generics.ListAPIView):
    serializer_class = MerchantGoodsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        merchant = get_object_or_404(Merchant, user=self.request.user)
        return MerchantGoods.objects.filter(merchant=merchant).select_related('goods', 'goods__category')


@method_decorator(csrf_exempt, name='dispatch')
class MerchantGoodsCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        merchant = get_object_or_404(Merchant, user=request.user)
        serializer = MerchantGoodsCreateSerializer(data=request.data)

        if serializer.is_valid():
            category = get_object_or_404(Category, pk=serializer.validated_data['category'])
            goods = Goods.objects.create(
                name=serializer.validated_data['name'],
                description=serializer.validated_data.get('description', ''),
                price=serializer.validated_data['price'],
                stock=serializer.validated_data['stock'],
                category=category,
                image=serializer.validated_data.get('image'),
            )
            MerchantGoods.objects.create(
                goods=goods, merchant=merchant,
                cost_price=serializer.validated_data.get('cost_price', 0),
                is_featured=serializer.validated_data.get('is_featured', False)
            )
            return Response({'success': True, 'message': '商品添加成功'}, status=201)
        return Response(serializer.errors, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class MerchantGoodsDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        merchant = get_object_or_404(Merchant, user=request.user)
        merchant_goods = get_object_or_404(MerchantGoods, pk=pk, merchant=merchant)
        goods = merchant_goods.goods

        if 'name' in request.data: goods.name = request.data['name']
        if 'description' in request.data: goods.description = request.data['description']
        if 'price' in request.data: goods.price = request.data['price']
        if 'stock' in request.data: goods.stock = request.data['stock']
        if 'is_active' in request.data: goods.is_active = request.data['is_active']
        if request.FILES.get('image'): goods.image = request.FILES['image']
        goods.save()

        if 'cost_price' in request.data: merchant_goods.cost_price = request.data['cost_price']
        if 'is_featured' in request.data: merchant_goods.is_featured = request.data['is_featured']
        merchant_goods.save()

        return Response({'success': True, 'message': '商品更新成功'})

    def delete(self, request, pk):
        merchant = get_object_or_404(Merchant, user=request.user)
        merchant_goods = get_object_or_404(MerchantGoods, pk=pk, merchant=merchant)
        goods = merchant_goods.goods
        merchant_goods.delete()
        goods.delete()
        return Response({'success': True, 'message': '商品已删除'})


@method_decorator(csrf_exempt, name='dispatch')
class MerchantOrderListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        merchant = get_object_or_404(Merchant, user=self.request.user)
        merchant_goods_ids = merchant.goods.values_list('goods_id', flat=True)
        return Order.objects.filter(items__goods_id__in=merchant_goods_ids).distinct()


@method_decorator(csrf_exempt, name='dispatch')
class MerchantOrderDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        merchant = get_object_or_404(Merchant, user=request.user)
        merchant_goods_ids = merchant.goods.values_list('goods_id', flat=True)
        order = get_object_or_404(Order, pk=pk, items__goods_id__in=merchant_goods_ids)
        from apps.orders.serializers import OrderSerializer
        return Response(OrderSerializer(order).data)


@method_decorator(csrf_exempt, name='dispatch')
class MerchantOrderShipAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        merchant = get_object_or_404(Merchant, user=request.user)
        merchant_goods_ids = merchant.goods.values_list('goods_id', flat=True)
        order = get_object_or_404(Order, pk=pk, items__goods_id__in=merchant_goods_ids)

        if order.status == 2:
            order.status = 3
            order.shipped_at = timezone.now()
            order.save()
            return Response({'success': True, 'message': '订单已发货'})
        return Response({'success': False, 'message': '该订单无法发货'}, status=400)
