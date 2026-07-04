from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Review
from .serializers import ReviewSerializer, CreateReviewSerializer
from apps.goods.models import Goods
from apps.orders.models import Order


@method_decorator(csrf_exempt, name='dispatch')
class ReviewListAPI(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        goods_id = self.kwargs.get('goods_id')
        return Review.objects.filter(goods_id=goods_id).select_related('user')


@method_decorator(csrf_exempt, name='dispatch')
class CreateReviewAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateReviewSerializer(data=request.data)
        if serializer.is_valid():
            goods_id = serializer.validated_data['goods_id']
            goods = get_object_or_404(Goods, pk=goods_id)

            if not Order.objects.filter(
                user=request.user, items__goods=goods, status__in=[2, 3, 4]
            ).exists():
                return Response({'success': False, 'message': '只有购买过该商品的用户才能评价'}, status=400)

            if Review.objects.filter(user=request.user, goods=goods).exists():
                return Response({'success': False, 'message': '您已经评价过该商品'}, status=400)

            order = Order.objects.filter(
                user=request.user, items__goods=goods, status__in=[2, 3, 4]
            ).first()

            if order:
                Review.objects.create(
                    user=request.user, goods=goods, order=order,
                    rating=serializer.validated_data['rating'],
                    content=serializer.validated_data.get('content', '')
                )
                return Response({'success': True, 'message': '评价成功'})
            else:
                return Response({'success': False, 'message': '未找到有效订单'}, status=400)
        return Response(serializer.errors, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteReviewAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        review = get_object_or_404(Review, pk=pk, user=request.user)
        review.delete()
        return Response({'success': True, 'message': '评价已删除'})
