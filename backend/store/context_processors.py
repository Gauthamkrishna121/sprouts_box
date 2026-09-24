from .models import SiteSettings, Product, Category
from django.db.models import Count

def site_settings(request):
    """
    Context processor to make SiteSettings and dynamic store metrics globally available.
    """
    try:
        settings_obj = SiteSettings.load()
    except Exception:
        settings_obj = None

    # Fetch live dynamic metrics for Admin Dashboard
    try:
        total_products = Product.objects.count()
        in_stock_products = Product.objects.filter(is_available=True).count()
        out_of_stock_products = Product.objects.filter(is_available=False).count()
        total_categories = Category.objects.count()
        recent_products = list(Product.objects.select_related('category').order_by('-created_at')[:6])
        categories_list = list(Category.objects.annotate(num_products=Count('products'))[:6])
    except Exception:
        total_products = 0
        in_stock_products = 0
        out_of_stock_products = 0
        total_categories = 0
        recent_products = []
        categories_list = []

    return {
        'site_settings': settings_obj,
        'admin_stats': {
            'total_products': total_products,
            'in_stock_products': in_stock_products,
            'out_of_stock_products': out_of_stock_products,
            'total_categories': total_categories,
            'recent_products': recent_products,
            'categories_list': categories_list,
        }
    }
