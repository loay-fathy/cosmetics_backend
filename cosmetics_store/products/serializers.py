from rest_framework import serializers
from .models import Product, Category, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text']

    def get_image_url(self, obj):
        try:
            return obj.image.url if obj.image else None
        except Exception:
            return None


class ProductSerializer(serializers.ModelSerializer):
    # Read-only nested category
    category = CategorySerializer(read_only=True)
    # Write-only category ID
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    # Nested product images
    images = ProductImageSerializer(many=True, read_only=True)
    # Explicitly handle Cloudinary URL for main image
    main_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price',
            'category', 'category_id', 'main_image_url','images'
        ]
        read_only_fields = ('id', 'created_at', 'category', 'updated_at')

    def get_main_image_url(self, obj):
        try:
            return obj.main_image.url if obj.main_image else None
        except Exception:
            return None
