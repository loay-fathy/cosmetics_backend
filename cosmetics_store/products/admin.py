from django.contrib import admin
from .models import Product, Category, ProductImage
from django.utils.html import format_html


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'product_count')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)
    ordering = ('name',)

    def product_count(self, obj):
        """Show how many products belong to this category."""
        return obj.products.count()
    product_count.short_description = "Products"


class ProductImageInline(admin.TabularInline):
    """Inline images for each product."""
    model = ProductImage
    extra = 1
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover; border-radius:6px;" />', obj.image.url)
        return "No image"
    preview_image.short_description = "Preview"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock', 'is_active', 'created_at', 'preview_main_image', 'is_best_seller')
    list_filter = ('category', 'is_active', 'is_best_seller', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_active', 'is_best_seller')
    list_per_page = 20
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'preview_main_image')
    inlines = [ProductImageInline]

    fieldsets = (
        ("Basic Info", {
            'fields': ('name', 'category', 'description', 'price', 'stock', 'is_active', 'is_best_seller')
        }),
        ("Images", {
            'fields': ('main_image', 'preview_main_image')
        }),
        ("Timestamps", {
            'fields': ('created_at',)
        }),
    )

    def preview_main_image(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="80" height="80" style="object-fit:cover; border-radius:6px;" />', obj.main_image.url)
        return "No image"
    preview_main_image.short_description = "Main Image Preview"
