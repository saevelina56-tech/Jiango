from rest_framework import serializers
from .models import Product, Category



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']


class NestedCategorySerializer(CategorySerializer):
    children_count = serializers.SerializerMethodField()
    
    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ['parent', 'children_count']
    
    def get_children_count(self, obj):
        return obj.children.count()



class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'price', 
            'category_name',
            'is_available',
            'stock_quantity'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = NestedCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'category',
            'category_id',
            'stock_quantity',
            'is_available',
            'popularity_score',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'popularity_score']
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена товара не может быть отрицательной.")
        return value
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название товара обязательно.")
        return value


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'category',
            'stock_quantity',
            'is_available'
        ]
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена товара не может быть отрицательной.")
        return value
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название товара обязательно.")
        return value