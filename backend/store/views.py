from django.shortcuts import render
from .models import Category, Product

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_available=True)[:5]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'home.html', context)


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

    context = {
        'categories': categories,
        'products': products,
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
