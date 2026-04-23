from rest_framework import serializers
from product_management.models import (
    Product,
    ProductImage,
    ProductType,
    ProductAttributes,
    InventoryChangeLog,
    StockAlert
)
from masters.models import (Attribute, AttributeValue, Category,)


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'


class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = '__all__'


class ProductAttributeSerializer(serializers.ModelSerializer):
    product_attrubute = AttributeSerializer(read_only=True, many=True)
    product_attrubute_variant = AttributeValueSerializer(
        many=True, read_only=True)

    class Meta:
        model = ProductAttributes
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug', ]


class ProductSerializer(serializers.ModelSerializer):
    product_images = ProductImageSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    product_type = ProductTypeSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class InventoryChangeLogSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = InventoryChangeLog
        fields = '__all__'


class StockAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    last_change_log_detail = InventoryChangeLogSerializer(source='last_change_log', read_only=True)

    class Meta:
        model = StockAlert
        fields = '__all__'


class StockAlertCountSerializer(serializers.Serializer):
    pending_count = serializers.IntegerField()


class ProductUpdateStockSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
    change_type = serializers.ChoiceField(choices=['increase', 'decrease'])
    reason = serializers.CharField(max_length=255, required=False, allow_blank=True)
