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
<<<<<<< Updated upstream
=======


def shop(request):
    category_slug = request.GET.get('category', '')
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '')

    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)

    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if search_query:
        products = products.filter(name__icontains=search_query)

    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')

    # Curated fallbacks if database has no products yet
    fallback_products = [
        {'name': 'Organic Tomatoes', 'category': 'Vegetables', 'price': 60, 'unit': 'kg', 'image': '/static/plugin/images/prod_tomatoes.png'},
        {'name': 'Fresh Green Spinach', 'category': 'Vegetables', 'price': 40, 'unit': 'bunch', 'image': '/static/plugin/images/prod_spinach.png'},
        {'name': 'Organic Bananas', 'category': 'Fruits', 'price': 50, 'unit': 'kg', 'image': '/static/plugin/images/prod_bananas.png'},
        {'name': 'Raw Honey', 'category': 'Natural Products', 'price': 280, 'unit': '500g', 'image': '/static/plugin/images/cat_natural.png'},
        {'name': 'Toor Dal', 'category': 'Grains & Pulses', 'price': 90, 'unit': 'kg', 'image': '/static/plugin/images/cat_grains.png'},
        {'name': 'Fresh Farm Combo', 'category': 'Combo Packs', 'price': 450, 'unit': 'box', 'image': '/static/plugin/images/cat_combos.png'},
        {'name': 'Assorted Fresh Fruits', 'category': 'Fruits', 'price': 220, 'unit': 'basket', 'image': '/static/plugin/images/cat_fruits.png'},
        {'name': 'Organic Crunchy Carrots', 'category': 'Vegetables', 'price': 75, 'unit': 'kg', 'image': '/static/plugin/images/cat_vegetables.png'},
    ]

    context = {
        'categories': categories,
        'products': products,
        'fallback_products': fallback_products,
        'selected_category': category_slug,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'shop.html', context)


def about(request):
    return render(request, 'about.html')


def contact(request):
    success_message = None
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        # Process message or store in DB/send email
        success_message = f"Thank you, {name}! Your message has been received. We will get back to you shortly."
    
    return render(request, 'contact.html', {'success_message': success_message})


>>>>>>> Stashed changes
