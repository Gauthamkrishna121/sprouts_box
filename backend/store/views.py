from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from urllib.parse import quote
from .models import Category, Product, Order, OrderItem, SiteSettings
from .cart import Cart


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


# --- Cart & Checkout Views ---

def cart_detail(request):
    """
    Renders the dedicated shopping cart page.
    """
    cart = Cart(request)
    summary = cart.get_summary()
    recommended_products = Product.objects.filter(is_available=True).order_by('-created_at')[:4]
    return render(request, 'cart.html', {
        'cart': cart,
        'summary': summary,
        'recommended_products': recommended_products,
    })


def cart_data(request):
    """
    Returns current cart state as JSON for dynamic slide-over drawer updates.
    """
    cart = Cart(request)
    return JsonResponse(cart.get_json_data())


@require_POST
def cart_add(request, product_id):
    """
    Add product to cart via AJAX or POST form.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    cart.add(product=product, quantity=quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        cart_info = cart.get_json_data()
        return JsonResponse({
            'success': True,
            'message': f"Added {product.name} to your basket!",
            'product_name': product.name,
            'cart': cart_info
        })

    return redirect('store:cart_detail')


@require_POST
def cart_update(request, product_id):
    """
    Update quantity of product in cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    cart.update(product_id=product.id, quantity=quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        cart_info = cart.get_json_data()
        return JsonResponse({
            'success': True,
            'message': f"Updated {product.name} quantity.",
            'cart': cart_info
        })

    return redirect('store:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """
    Remove product from cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product_id=product.id)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        cart_info = cart.get_json_data()
        return JsonResponse({
            'success': True,
            'message': f"Removed {product.name} from basket.",
            'cart': cart_info
        })

    return redirect('store:cart_detail')


@require_POST
def cart_clear(request):
    """
    Clear all items in cart.
    """
    cart = Cart(request)
    cart.clear()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'message': "Cart cleared successfully.",
            'cart': cart.get_json_data()
        })

    return redirect('store:shop')


def checkout(request):
    """
    Process checkout and place an order.
    """
    cart = Cart(request)
    summary = cart.get_summary()

    if len(cart) == 0:
        return redirect('store:shop')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip()
        delivery_address = request.POST.get('delivery_address', '').strip()
        city = request.POST.get('city', 'Kerala').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        delivery_notes = request.POST.get('delivery_notes', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')

        if not full_name or not phone_number or not delivery_address:
            error_msg = "Please fill in your name, phone number, and delivery address."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            return render(request, 'cart.html', {
                'cart': cart,
                'summary': summary,
                'error_message': error_msg
            })

        # Create Order
        order = Order.objects.create(
            full_name=full_name,
            phone_number=phone_number,
            email=email if email else None,
            delivery_address=delivery_address,
            city=city,
            postal_code=postal_code,
            delivery_notes=delivery_notes,
            subtotal=summary['subtotal'],
            shipping_fee=summary['shipping'],
            total_amount=summary['total'],
            payment_method=payment_method,
            status='pending',
        )

        # Create OrderItems
        items_summary_text = []
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['name'],
                price=item['price'],
                quantity=item['quantity'],
                unit=item.get('unit', '1 kg'),
            )
            items_summary_text.append(f"• {item['quantity']}x {item['name']} ({item.get('unit', '')}) - ₹{item['total_price']:.2f}")

        # Construct WhatsApp Link for Customer & Store
        site_settings = SiteSettings.load()
        store_phone = "".join(filter(str.isdigit, site_settings.phone_number or "919876543210"))
        if not store_phone.startswith('91') and len(store_phone) == 10:
            store_phone = '91' + store_phone

        items_formatted = "%0A".join([quote(line) for line in items_summary_text])
        whatsapp_message = (
            f"*🌱 New Order from Sprouts Box!*%0A%0A"
            f"*Order Number:* %23{order.order_number}%0A"
            f"*Customer:* {quote(order.full_name)} ({order.phone_number})%0A"
            f"*Delivery Address:* {quote(order.delivery_address)}, {quote(order.city)} {quote(order.postal_code or '')}%0A"
            f"*Payment Method:* {quote(order.get_payment_method_display())}%0A%0A"
            f"*Items Ordered:*%0A{items_formatted}%0A%0A"
            f"*Subtotal:* ₹{order.subtotal:.2f}%0A"
            f"*Delivery Fee:* {'FREE' if order.shipping_fee == 0 else f'₹{order.shipping_fee:.2f}'}%0A"
            f"*Grand Total:* *₹{order.total_amount:.2f}*%0A%0A"
            f"Please confirm my order delivery. Thank you!"
        )
        whatsapp_url = f"https://wa.me/{store_phone}?text={whatsapp_message}"

        # Clear cart
        cart.clear()

        # Store order id in session for order confirmation page
        request.session['latest_order_id'] = order.id
        request.session['latest_order_number'] = order.order_number
        request.session['whatsapp_url'] = whatsapp_url

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'success': True,
                'order_number': order.order_number,
                'redirect_url': f"/order-success/?order={order.order_number}",
                'whatsapp_url': whatsapp_url,
            })

        return redirect(f"/order-success/?order={order.order_number}")

    return redirect('store:cart_detail')


def order_success(request):
    """
    Renders order confirmation page.
    """
    order_number = request.GET.get('order') or request.session.get('latest_order_number')
    if not order_number:
        return redirect('store:home')

    order = get_object_or_404(Order, order_number=order_number)
    whatsapp_url = request.session.get('whatsapp_url')

    if not whatsapp_url:
        site_settings = SiteSettings.load()
        store_phone = "".join(filter(str.isdigit, site_settings.phone_number or "919876543210"))
        if not store_phone.startswith('91') and len(store_phone) == 10:
            store_phone = '91' + store_phone
        items_summary_text = [
            f"• {item.quantity}x {item.product_name} ({item.unit}) - ₹{item.get_total_price():.2f}"
            for item in order.items.all()
        ]
        items_formatted = "%0A".join([quote(line) for line in items_summary_text])
        whatsapp_message = (
            f"*🌱 Order Confirmation - Sprouts Box*%0A%0A"
            f"*Order Number:* %23{order.order_number}%0A"
            f"*Customer:* {quote(order.full_name)} ({order.phone_number})%0A"
            f"*Delivery Address:* {quote(order.delivery_address)}, {quote(order.city)}%0A%0A"
            f"*Items:*%0A{items_formatted}%0A%0A"
            f"*Total:* *₹{order.total_amount:.2f}*%0A"
        )
        whatsapp_url = f"https://wa.me/{store_phone}?text={whatsapp_message}"

    return render(request, 'order_success.html', {
        'order': order,
        'whatsapp_url': whatsapp_url,
    })

