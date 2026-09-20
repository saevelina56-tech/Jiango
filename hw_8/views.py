from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .models import Product, Category
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    CategorySerializer,
)
from .filters import ProductFilter
from .permissions import IsAdminOrReadOnly


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'popularity_score', 'name']
    ordering = ['-created_at']
    
    permission_classes = [IsAdminOrReadOnly]
    
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        limit = int(request.query_params.get('limit', 10))
        popular_products = self.queryset.order_by('-popularity_score')[:limit]
        serializer = ProductListSerializer(popular_products, many=True, context={'request': request})
        return Response(serializer.data)



class ProductsByCategoryView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get(self, request, category_slug):
        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            return Response(
                {'error': 'Категория не найдена'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        products = Product.objects.filter(
            category=category,
            is_available=True
        ).select_related('category')
        
        price_min = request.query_params.get('price_min')
        price_max = request.query_params.get('price_max')
        
        if price_min:
            products = products.filter(price__gte=price_min)
        if price_max:
            products = products.filter(price__lte=price_max)
        
        page_size = int(request.query_params.get('page_size', 20))
        page_number = int(request.query_params.get('page', 1))
        
        start = (page_number - 1) * page_size
        end = start + page_size
        
        paginated_products = products[start:end]
        serializer = ProductListSerializer(paginated_products, many=True, context={'request': request})
        
        response_data = {
            'count': products.count(),
            'next': f'?page={page_number + 1}&page_size={page_size}' if end < products.count() else None,
            'previous': f'?page={page_number - 1}&page_size={page_size}' if page_number > 1 else None,
            'results': serializer.data
        }
        
        return Response(response_data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]