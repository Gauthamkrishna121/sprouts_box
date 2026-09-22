from django.shortcuts import render
from .models import Category, Product

def home(request):
    categories = Category.objects.all()
    # Fetch some sample featured products if any exist
    featured_products = Product.objects.filter(is_available=True)[:5]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'home.html', context)
