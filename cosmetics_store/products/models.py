from django.db import models
from cloudinary.models import CloudinaryField # <--- Import this

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    # Optional: Add Meta for ordering and correct plural name
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Categories"


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_best_seller = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    main_image = CloudinaryField(
        'image', # This tells Cloudinary to treat it as an image
        folder='products/main_images/',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: Add Meta for default ordering
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    
    # <--- CHANGED
    image = CloudinaryField(
        'image',
        folder='products/extra_images/'
    )
    
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"