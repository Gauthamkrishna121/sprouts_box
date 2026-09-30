from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Category, Product, SiteSettings, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count', 'category_actions')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    ordering = ('name',)

    def product_count(self, obj):
        count = obj.products.count()
        return format_html(
            '<span class="badge-count">{} products</span>',
            count
        )
    product_count.short_description = "Products"

    def category_actions(self, obj):
        edit_url = reverse('admin:store_category_change', args=[obj.pk])
        delete_url = reverse('admin:store_category_delete', args=[obj.pk])
        return format_html(
            '<div class="admin-row-actions">'
            '  <a href="{}" class="action-btn edit-btn" title="Edit Category">✏️ Edit</a>'
            '  <a href="{}" class="action-btn delete-btn" title="Delete Category">🗑️ Delete</a>'
            '</div>',
            edit_url,
            delete_url
        )
    category_actions.short_description = "Actions"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail',
        'name',
        'category',
        'formatted_price',
        'unit',
        'availability_badge',
        'is_available',
        'updated_at',
        'product_actions'
    )
    list_filter = ('category', 'is_available', 'created_at')
    list_editable = ('is_available',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_per_page = 20
    ordering = ('-created_at',)

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" class="admin-table-thumb" alt="{}" />',
                obj.image.url,
                obj.name
            )
        return mark_safe('<div class="admin-table-thumb-placeholder">🌱</div>')
    image_thumbnail.short_description = "Image"

    def formatted_price(self, obj):
        return format_html('<span class="admin-price">₹{}</span>', obj.price)
    formatted_price.short_description = "Price"

    def availability_badge(self, obj):
        if obj.is_available:
            return mark_safe('<span class="status-badge in-stock">● In Stock</span>')
        return mark_safe('<span class="status-badge out-of-stock">○ Out of Stock</span>')
    availability_badge.short_description = "Stock Status"

    def product_actions(self, obj):
        edit_url = reverse('admin:store_product_change', args=[obj.pk])
        delete_url = reverse('admin:store_product_delete', args=[obj.pk])
        return format_html(
            '<div class="admin-row-actions">'
            '  <a href="{}" class="action-btn edit-btn" title="Edit Product">✏️ Edit</a>'
            '  <a href="{}" class="action-btn delete-btn" title="Delete Product">🗑️ Delete</a>'
            '</div>',
            edit_url,
            delete_url
        )
    product_actions.short_description = "Actions"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('📞 Contact Details', {
            'fields': (
                ('phone_number', 'phone_hours'),
                ('email_address', 'email_note'),
                ('address_line1', 'address_line2'),
            ),
            'description': 'Manage contact details displayed on the Contact page and Footer.'
        }),
        ('💬 Contact Page Headings & Text', {
            'fields': (
                ('contact_subtitle', 'contact_title'),
                'contact_intro',
            ),
            'description': 'Manage headings and introductory text on the Contact page.'
        }),
        ('🌐 Social Media Links', {
            'fields': (
                ('instagram_url', 'facebook_url'),
                ('youtube_url', 'whatsapp_url'),
            ),
            'description': 'Configure social media icons and profile links.'
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return self.change_view(request, str(obj.pk), extra_context=extra_context)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity', 'unit', 'item_total')
    can_delete = False

    def item_total(self, obj):
        if obj.pk:
            return format_html('<strong>₹{}</strong>', obj.get_total_price())
        return '-'
    item_total.short_description = "Line Total"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'full_name',
        'phone_number',
        'items_count',
        'formatted_total',
        'payment_method_badge',
        'status_badge',
        'created_at',
        'order_actions'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'full_name', 'phone_number', 'email', 'delivery_address')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'subtotal', 'shipping_fee', 'total_amount')
    inlines = [OrderItemInline]
    list_per_page = 25
    ordering = ('-created_at',)

    fieldsets = (
        ('📦 Order Summary', {
            'fields': (
                ('order_number', 'status'),
                ('payment_method',),
                ('subtotal', 'shipping_fee', 'total_amount'),
                ('created_at', 'updated_at'),
            )
        }),
        ('👤 Customer & Delivery Details', {
            'fields': (
                ('full_name', 'phone_number'),
                'email',
                'delivery_address',
                ('city', 'postal_code'),
                'delivery_notes',
            )
        }),
    )

    def items_count(self, obj):
        count = obj.items.count()
        return format_html('<span class="badge-count">{} items</span>', count)
    items_count.short_description = "Items"

    def formatted_total(self, obj):
        return format_html('<span class="admin-price">₹{}</span>', obj.total_amount)
    formatted_total.short_description = "Total"

    def payment_method_badge(self, obj):
        label = dict(Order.PAYMENT_CHOICES).get(obj.payment_method, obj.payment_method)
        return format_html('<span class="status-badge" style="background:#f0fdf4;color:#166534;border:1px solid #bbf7d0;">💳 {}</span>', label)
    payment_method_badge.short_description = "Payment"

    def status_badge(self, obj):
        colors = {
            'pending': ('#fef3c7', '#92400e', '#fde68a'),
            'confirmed': ('#e0f2fe', '#075985', '#bae6fd'),
            'out_for_delivery': ('#ede9fe', '#5b21b6', '#ddd6fe'),
            'delivered': ('#dcfce7', '#166534', '#bbf7d0'),
            'cancelled': ('#fee2e2', '#991b1b', '#fecaca'),
        }
        bg, text, border = colors.get(obj.status, ('#f3f4f6', '#374151', '#e5e7eb'))
        label = dict(Order.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(
            '<span class="status-badge" style="background:{};color:{};border:1px solid {};font-weight:600;">{}</span>',
            bg, text, border, label
        )
    status_badge.short_description = "Status"

    def order_actions(self, obj):
        edit_url = reverse('admin:store_order_change', args=[obj.pk])
        return format_html(
            '<div class="admin-row-actions">'
            '  <a href="{}" class="action-btn edit-btn" title="View/Edit Order">👁️ View Order</a>'
            '</div>',
            edit_url
        )
    order_actions.short_description = "Actions"



