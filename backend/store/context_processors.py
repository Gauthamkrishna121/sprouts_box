from .models import SiteSettings, Product, Category, Order
from django.db.models import Count

def site_settings(request):
    """
    Context processor to make SiteSettings globally available.
    Admin inventory metrics are computed ONLY for admin paths (/admin/).
    """
    try:
        settings_obj = SiteSettings.load()
    except Exception:
        settings_obj = None

    admin_stats = {
        'total_products': 0,
        'in_stock_products': 0,
        'out_of_stock_products': 0,
        'out_of_stock_list': [],
        'total_categories': 0,
        'recent_products': [],
        'categories_list': [],
        'total_orders': 0,
        'pending_orders': 0,
    }

    # Only execute expensive admin analytics queries when accessing the Django admin dashboard
    if hasattr(request, 'path') and request.path.startswith('/admin/'):
        try:
            admin_stats = {
                'total_products': Product.objects.count(),
                'in_stock_products': Product.objects.filter(is_available=True).count(),
                'out_of_stock_products': Product.objects.filter(is_available=False).count(),
                'out_of_stock_list': list(Product.objects.filter(is_available=False).select_related('category')[:6]),
                'total_categories': Category.objects.count(),
                'recent_products': list(Product.objects.select_related('category').order_by('-created_at')[:6]),
                'categories_list': list(Category.objects.annotate(num_products=Count('products'))[:6]),
                'total_orders': Order.objects.count(),
                'pending_orders': Order.objects.filter(status='pending').count(),
            }
        except Exception:
            pass

    return {
        'site_settings': settings_obj,
        'admin_stats': admin_stats,
    }


def cart_context(request):
    """
    Context processor to make current user's session Cart available in all templates.
    """
    from .cart import Cart
    if hasattr(request, 'session'):
        try:
            cart = Cart(request)
            return {
                'cart': cart,
                'cart_summary': cart.get_summary()
            }
        except Exception:
            pass
    return {
        'cart': None,
        'cart_summary': None
    }

