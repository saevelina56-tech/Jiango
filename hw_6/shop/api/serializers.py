from rest_framework import serializers
from shop.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock', 'category')


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'price', 'stock',
            'category', 'category_id',
            'is_popular', 'created_at',
        )
        read_only_fields = ('created_at',)

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Название товара обязательно.')
        return value.strip()

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Цена не может быть отрицательной.')
        return value