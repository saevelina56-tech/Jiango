from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from shop.models import Category, Product
from .serializers import ProductListSerializer

from rest_framework import viewsets
from rest_framework.decorators import action
from .serializers import ProductListSerializer, ProductDetailSerializer
from .filters import ProductFilter


class ProductsByCategoryView(APIView):

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        products = category.products.all()

        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        in_stock = request.query_params.get('in_stock')

        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        if in_stock == 'true':
            products = products.filter(stock__gt=0)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    filterset_class = ProductFilter
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action == 'retrieve':
            return ProductDetailSerializer
        if self.action == 'popular':
            return ProductListSerializer
        return ProductDetailSerializer  

    @action(detail=False, methods=['get'], url_path='popular')
    def popular(self, request):
        qs = self.get_queryset().filter(is_popular=True, stock__gt=0)[:10]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)