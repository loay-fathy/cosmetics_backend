from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from .permissions import IsAdminOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'  # optional: allow /categories/<slug>/

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]  # admin-only for unsafe methods

    filter_backends = [
        DjangoFilterBackend,  # precise filtering
        filters.SearchFilter,  # search by text
        filters.OrderingFilter,  # ordering
    ]

    # fields users can filter by ?category=makeup or ?category__slug=makeup
    filterset_fields = ['category__slug', 'category', 'price', 'stock']

    # search: full-text-like search on these fields:
    search_fields = ['name', 'description', 'category__name']

    # allow ordering: ?ordering=price or ?ordering=-created_at
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def best_sellers(self, request):
        # Get all best sellers
        best_sellers = list(self.get_queryset().filter(is_best_seller=True))
        count = len(best_sellers)

        if count < 4:
            # Fill the rest with latest non-best-seller products
            fillers = list(
                self.get_queryset()
                .exclude(id__in=[p.id for p in best_sellers])
                .order_by('-created_at')[: (4 - count)]
            )
            best_sellers.extend(fillers)

        serializer = self.get_serializer(best_sellers[:4], many=True)
        return Response(serializer.data)