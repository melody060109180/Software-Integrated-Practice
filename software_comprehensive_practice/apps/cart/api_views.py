from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer
from apps.goods.models import Goods


@method_decorator(csrf_exempt, name='dispatch')
class CartDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class CartAddAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            goods_id = serializer.validated_data['goods_id']
            quantity = serializer.validated_data['quantity']
            
            goods = get_object_or_404(Goods, pk=goods_id, is_active=True)
            
            if quantity > goods.stock:
                return Response({
                    'success': False,
                    'message': '库存不足'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, goods=goods,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                if cart_item.quantity > goods.stock:
                    return Response({
                        'success': False,
                        'message': '库存不足'
                    }, status=status.HTTP_400_BAD_REQUEST)
                cart_item.save()
            
            return Response({
                'success': True,
                'message': '已添加到购物车',
                'cart_count': cart.total_quantity
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class CartItemUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, item_id):
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        serializer = UpdateCartItemSerializer(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            if quantity > cart_item.goods.stock:
                return Response({
                    'success': False,
                    'message': '库存不足'
                }, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = quantity
            cart_item.save()
            return Response({'success': True, 'message': '购物车已更新'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, item_id):
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        cart_item.delete()
        return Response({'success': True, 'message': '商品已移除'})


@method_decorator(csrf_exempt, name='dispatch')
class CartClearAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({'success': True, 'message': '购物车已清空'})
