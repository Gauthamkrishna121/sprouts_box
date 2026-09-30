from decimal import Decimal
from django.conf import settings
from .models import Product

CART_SESSION_ID = 'sprouts_cart'
FREE_SHIPPING_THRESHOLD = Decimal('499.00')
STANDARD_SHIPPING_FEE = Decimal('40.00')


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        quantity = max(1, int(quantity))
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
                'name': product.name,
                'unit': product.unit,
                'image_url': product.image.url if product.image else '/static/plugin/images/prod_tomatoes.png',
                'slug': product.slug,
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
            
        self.save()

    def update(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            qty = int(quantity)
            if qty <= 0:
                self.remove(product_id)
            else:
                self.cart[product_id]['quantity'] = qty
                self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        if CART_SESSION_ID in self.session:
            del self.session[CART_SESSION_ID]
        self.cart = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = list(self.cart.keys())
        products = Product.objects.filter(id__in=product_ids)
        product_map = {str(p.id): p for p in products}

        for p_id, item_data in list(self.cart.items()):
            product = product_map.get(p_id)
            if not product or not product.is_available:
                continue

            price = Decimal(item_data.get('price', product.price))
            quantity = item_data.get('quantity', 1)
            total_price = price * quantity

            item_copy = item_data.copy()
            item_copy['product'] = product
            item_copy['price'] = price
            item_copy['total_price'] = total_price
            item_copy['product_id'] = int(p_id)
            yield item_copy

    def __len__(self):
        return sum(item.get('quantity', 0) for item in self.cart.values())

    def get_subtotal(self):
        subtotal = Decimal('0.00')
        for item in self.cart.values():
            price = Decimal(item.get('price', '0'))
            qty = item.get('quantity', 0)
            subtotal += price * qty
        return subtotal

    def get_summary(self):
        subtotal = self.get_subtotal()
        total_items = len(self)
        if total_items == 0:
            shipping = Decimal('0.00')
            amount_needed = FREE_SHIPPING_THRESHOLD
            has_free_shipping = False
        else:
            if subtotal >= FREE_SHIPPING_THRESHOLD:
                shipping = Decimal('0.00')
                amount_needed = Decimal('0.00')
                has_free_shipping = True
            else:
                shipping = STANDARD_SHIPPING_FEE
                amount_needed = FREE_SHIPPING_THRESHOLD - subtotal
                has_free_shipping = False

        total = subtotal + shipping
        progress_percentage = min(100, int((subtotal / FREE_SHIPPING_THRESHOLD) * 100)) if FREE_SHIPPING_THRESHOLD > 0 else 100

        return {
            'subtotal': subtotal,
            'shipping': shipping,
            'total': total,
            'total_items': total_items,
            'free_shipping_threshold': FREE_SHIPPING_THRESHOLD,
            'amount_needed_for_free_shipping': amount_needed,
            'has_free_shipping': has_free_shipping,
            'free_shipping_progress': progress_percentage,
        }

    def get_json_data(self):
        summary = self.get_summary()
        items_list = []
        for item in self:
            items_list.append({
                'id': item['product_id'],
                'name': item['name'],
                'price': str(item['price']),
                'formatted_price': f"₹{item['price']:.2f}",
                'quantity': item['quantity'],
                'unit': item.get('unit', '1 kg'),
                'total_price': str(item['total_price']),
                'formatted_total_price': f"₹{item['total_price']:.2f}",
                'image_url': item.get('image_url') or '/static/plugin/images/prod_tomatoes.png',
                'url': f"/shop/?q={item.get('slug', '')}"
            })

        return {
            'cart_count': summary['total_items'],
            'subtotal': f"{summary['subtotal']:.2f}",
            'formatted_subtotal': f"₹{summary['subtotal']:.2f}",
            'shipping': f"{summary['shipping']:.2f}",
            'formatted_shipping': "FREE" if summary['has_free_shipping'] else f"₹{summary['shipping']:.2f}",
            'total': f"{summary['total']:.2f}",
            'formatted_total': f"₹{summary['total']:.2f}",
            'has_free_shipping': summary['has_free_shipping'],
            'amount_needed': f"{summary['amount_needed_for_free_shipping']:.2f}",
            'free_shipping_progress': summary['free_shipping_progress'],
            'items': items_list,
        }
