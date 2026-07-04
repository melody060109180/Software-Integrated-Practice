from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from .models import Category, Goods
from .serializers import CategorySerializer, GoodsSerializer, GoodsListSerializer


@method_decorator(csrf_exempt, name='dispatch')
class CategoryListAPI(generics.ListAPIView):
    queryset = Category.objects.filter(parent=None)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDetailAPI(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


@method_decorator(csrf_exempt, name='dispatch')
class GoodsListAPI(generics.ListAPIView):
    serializer_class = GoodsListSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'sales', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Goods.objects.filter(is_active=True)
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


@method_decorator(csrf_exempt, name='dispatch')
class GoodsDetailAPI(generics.RetrieveAPIView):
    queryset = Goods.objects.filter(is_active=True)
    serializer_class = GoodsSerializer
    permission_classes = [AllowAny]
