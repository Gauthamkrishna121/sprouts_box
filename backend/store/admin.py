from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
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
        'price',
        'unit',
        'availability_badge',
        'is_available',
        'updated_at',
        'product_actions'
    )
    list_display_links = ('name',)
    list_editable = ('price', 'unit', 'is_available')
    list_filter = ('is_available', 'category', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'category__name', 'slug')
    search_help_text = "Search products by name, description, category, or slug"
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    actions = ['mark_as_available', 'mark_as_unavailable', 'duplicate_products']

    class Media:
        js = ('js/admin_product_preview.js',)

    fieldsets = (
        ('🌿 Basic Information', {
            'fields': (
                ('name', 'slug'),
                'category',
                'description',
            ),
            'description': 'Product identification, permalink slug, and category assignment.'
        }),
        ('💰 Pricing & Packaging', {
            'fields': (
                ('price', 'unit'),
            ),
            'description': 'Set customer retail price and selling unit.'
        }),
        ('📦 Inventory & Stock Status', {
            'fields': (
                'is_available',
            ),
            'description': 'Control storefront availability. When unchecked, product is flagged as Out of Stock.'
        }),
        ('🖼️ Product Media & Photography', {
            'fields': (
                'image_preview',
                'image',
            ),
            'description': 'Upload high-resolution produce photography for store cards and product listings.'
        }),
        ('⏱️ Audit Log & Timestamps', {
            'fields': (
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse',),
            'description': 'System managed audit timestamps.'
        }),
    )

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<div class="admin-table-thumb-wrap">'
                '  <img src="{}" class="admin-table-thumb" alt="{}" />'
                '  <div class="admin-thumb-hover-preview">'
                '    <img src="{}" alt="{}" />'
                '    <div class="thumb-hover-info">'
                '      <div class="hover-title">{}</div>'
                '      <div class="hover-meta">₹{} / {}</div>'
                '    </div>'
                '  </div>'
                '</div>',
                obj.image.url,
                obj.name,
                obj.image.url,
                obj.name,
                obj.name,
                obj.price,
                obj.unit
            )
        return mark_safe('<div class="admin-table-thumb-placeholder" title="No image uploaded">🌱</div>')
    image_thumbnail.short_description = "Photo"

    def availability_badge(self, obj):
        if obj.is_available:
            return mark_safe('<span class="status-badge in-stock"><span class="badge-dot green"></span>In Stock</span>')
        return mark_safe('<span class="status-badge out-of-stock"><span class="badge-dot red"></span>Out of Stock</span>')
    availability_badge.short_description = "Stock Badge"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div class="admin-image-preview-card">'
                '  <div class="preview-img-container">'
                '    <img src="{}" alt="{}" class="form-preview-thumb" />'
                '  </div>'
                '  <div class="preview-details">'
                '    <div class="preview-status-tag">✓ Active Product Image</div>'
                '    <a href="{}" target="_blank" class="preview-full-link">Open Full Size Image ↗</a>'
                '  </div>'
                '</div>',
                obj.image.url,
                obj.name,
                obj.image.url
            )
        return mark_safe(
            '<div class="admin-image-preview-card empty">'
            '  <div class="preview-empty-icon">📷</div>'
            '  <p>No image currently uploaded for this product.</p>'
            '  <small>Select a file below to preview and upload.</small>'
            '</div>'
        )
    image_preview.short_description = "Current Image Preview"

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

    @admin.action(description="🌱 Mark selected products as In Stock")
    def mark_as_available(self, request, queryset):
        count = queryset.update(is_available=True)
        self.message_user(request, f"Successfully marked {count} product(s) as In Stock.")

    @admin.action(description="⚠️ Mark selected products as Out of Stock")
    def mark_as_unavailable(self, request, queryset):
        count = queryset.update(is_available=False)
        self.message_user(request, f"Successfully marked {count} product(s) as Out of Stock.")

    @admin.action(description="📋 Duplicate selected product(s)")
    def duplicate_products(self, request, queryset):
        import uuid
        count = 0
        for obj in queryset:
            unique_suffix = uuid.uuid4().hex[:5]
            new_slug = f"{obj.slug}-copy-{unique_suffix}"
            Product.objects.create(
                category=obj.category,
                name=f"{obj.name} (Copy)",
                slug=new_slug,
                description=obj.description,
                price=obj.price,
                unit=obj.unit,
                image=obj.image,
                is_available=False
            )
            count += 1
        self.message_user(request, f"Successfully duplicated {count} product(s) as draft copies.")


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
        'delivery_quick_action',
        'order_number',
        'status_badge',
        'full_name',
        'phone_number',
        'items_count',
        'formatted_total',
        'payment_method_badge',
        'created_at',
        'order_actions'
    )
    list_display_links = ('order_number',)
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'full_name', 'phone_number', 'email', 'delivery_address')
    readonly_fields = (
        'order_number',
        'delivery_pipeline_status',
        'created_at',
        'updated_at',
        'subtotal',
        'shipping_fee',
        'total_amount'
    )
    inlines = [OrderItemInline]
    list_per_page = 25
    ordering = ('-created_at',)
    actions = [
        'mark_as_confirmed',
        'mark_as_out_for_delivery',
        'mark_as_delivered',
        'mark_as_cancelled',
        'mark_as_pending',
    ]

    class Media:
        js = ('js/admin_order_status.js',)

    fieldsets = (
        ('🚚 Live Delivery Pipeline', {
            'fields': (
                'delivery_pipeline_status',
            ),
            'description': 'Live pipeline tracker. Click any stage to instantly transition order status.'
        }),
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

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        from django.db.models import Count
        status_counts = dict(
            Order.objects.values('status').annotate(total=Count('id')).values_list('status', 'total')
        )
        total_orders = Order.objects.count()
        current_status = request.GET.get('status__exact', '')
        current_payment = request.GET.get('payment_method__exact', '')

        def build_url(status=None, payment=None):
            q_dict = request.GET.copy()
            if 'p' in q_dict:
                del q_dict['p']
            if status is not None:
                if status == '':
                    q_dict.pop('status__exact', None)
                else:
                    q_dict['status__exact'] = status
            if payment is not None:
                if payment == '':
                    q_dict.pop('payment_method__exact', None)
                else:
                    q_dict['payment_method__exact'] = payment
            qs = q_dict.urlencode()
            return f"?{qs}" if qs else "?"

        extra_context['order_total_count'] = total_orders
        extra_context['current_status'] = current_status
        extra_context['current_payment'] = current_payment
        extra_context['order_status_tabs'] = [
            {
                'key': '',
                'label': 'All Orders',
                'icon': '📦',
                'count': total_orders,
                'url': build_url(status=''),
                'is_active': not current_status or current_status == '',
                'badge_class': 'tab-all',
            },
            {
                'key': 'pending',
                'label': 'Pending',
                'icon': '⏳',
                'count': status_counts.get('pending', 0),
                'url': build_url(status='pending'),
                'is_active': current_status == 'pending',
                'badge_class': 'tab-pending',
            },
            {
                'key': 'confirmed',
                'label': 'Confirmed',
                'icon': '📋',
                'count': status_counts.get('confirmed', 0),
                'url': build_url(status='confirmed'),
                'is_active': current_status == 'confirmed',
                'badge_class': 'tab-confirmed',
            },
            {
                'key': 'out_for_delivery',
                'label': 'Out for Delivery',
                'icon': '🚚',
                'count': status_counts.get('out_for_delivery', 0),
                'url': build_url(status='out_for_delivery'),
                'is_active': current_status == 'out_for_delivery',
                'badge_class': 'tab-out-for-delivery',
            },
            {
                'key': 'delivered',
                'label': 'Delivered',
                'icon': '✓',
                'count': status_counts.get('delivered', 0),
                'url': build_url(status='delivered'),
                'is_active': current_status == 'delivered',
                'badge_class': 'tab-delivered',
            },
            {
                'key': 'cancelled',
                'label': 'Cancelled',
                'icon': '❌',
                'count': status_counts.get('cancelled', 0),
                'url': build_url(status='cancelled'),
                'is_active': current_status == 'cancelled',
                'badge_class': 'tab-cancelled',
            },
        ]
        extra_context['payment_filter_options'] = [
            {'label': 'All Payments', 'url': build_url(payment=''), 'is_active': not current_payment},
            {'label': '💵 Cash on Delivery', 'url': build_url(payment='cod'), 'is_active': current_payment == 'cod'},
            {'label': '💳 Online Payment', 'url': build_url(payment='online'), 'is_active': current_payment == 'online'},
        ]
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:order_id>/quick-status/<str:new_status>/',
                self.admin_site.admin_view(self.quick_status_change),
                name='store_order_quick_status',
            ),
        ]
        return custom_urls + urls

    def quick_status_change(self, request, order_id, new_status):
        if not self.has_change_permission(request):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        valid_statuses = dict(Order.STATUS_CHOICES)
        if new_status in valid_statuses:
            order = get_object_or_404(Order, pk=order_id)
            old_label = order.get_status_display()
            order.status = new_status
            order.save(update_fields=['status', 'updated_at'])
            new_label = order.get_status_display()
            self.message_user(
                request,
                f"Order #{order.order_number} status updated: {old_label} ➔ {new_label}.",
                messages.SUCCESS
            )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
                return JsonResponse({
                    'success': True,
                    'order_id': order.pk,
                    'order_number': order.order_number,
                    'status': new_status,
                    'status_label': new_label,
                })
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return HttpResponseRedirect(referer)
        return HttpResponseRedirect(reverse('admin:store_order_changelist'))

    @admin.action(description="📋 Mark selected orders as Confirmed")
    def mark_as_confirmed(self, request, queryset):
        count = queryset.update(status='confirmed')
        self.message_user(request, f"Successfully marked {count} order(s) as Confirmed.")

    @admin.action(description="🚚 Mark selected orders as Out for Delivery")
    def mark_as_out_for_delivery(self, request, queryset):
        count = queryset.update(status='out_for_delivery')
        self.message_user(request, f"Successfully marked {count} order(s) as Out for Delivery.")

    @admin.action(description="📦 Mark selected orders as Delivered")
    def mark_as_delivered(self, request, queryset):
        count = queryset.update(status='delivered')
        self.message_user(request, f"Successfully marked {count} order(s) as Delivered.")

    @admin.action(description="❌ Mark selected orders as Cancelled")
    def mark_as_cancelled(self, request, queryset):
        count = queryset.update(status='cancelled')
        self.message_user(request, f"Successfully marked {count} order(s) as Cancelled.")

    @admin.action(description="⏳ Mark selected orders as Pending")
    def mark_as_pending(self, request, queryset):
        count = queryset.update(status='pending')
        self.message_user(request, f"Successfully marked {count} order(s) as Pending.")

    def items_count(self, obj):
        count = obj.items.count()
        return format_html('<span class="badge-count">{} items</span>', count)
    items_count.short_description = "Items"

    def formatted_total(self, obj):
        return format_html('<span class="admin-price">₹{}</span>', obj.total_amount)
    formatted_total.short_description = "Total"
    formatted_total.admin_order_field = "total_amount"

    def payment_method_badge(self, obj):
        label = dict(Order.PAYMENT_CHOICES).get(obj.payment_method, obj.payment_method)
        return format_html('<span class="status-badge" style="background:#f0fdf4;color:#166534;border:1px solid #bbf7d0;">💳 {}</span>', label)
    payment_method_badge.short_description = "Payment"
    payment_method_badge.admin_order_field = "payment_method"

    def status_badge(self, obj):
        colors = {
            'pending': ('#fef3c7', '#92400e', '#fde68a', '⏳'),
            'confirmed': ('#e0f2fe', '#075985', '#bae6fd', '📋'),
            'out_for_delivery': ('#ede9fe', '#5b21b6', '#ddd6fe', '🚚'),
            'delivered': ('#dcfce7', '#166534', '#bbf7d0', '📦'),
            'cancelled': ('#fee2e2', '#991b1b', '#fecaca', '❌'),
        }
        bg, text, border, icon = colors.get(obj.status, ('#f3f4f6', '#374151', '#e5e7eb', '•'))
        label = dict(Order.STATUS_CHOICES).get(obj.status, obj.status)

        options_html = []
        for code, name in Order.STATUS_CHOICES:
            active_class = "order-status-opt current" if code == obj.status else "order-status-opt"
            bullet = "✓ " if code == obj.status else ""
            url = reverse('admin:store_order_quick_status', args=[obj.pk, code])
            options_html.append(
                f'<a href="{url}" class="{active_class}" data-order-id="{obj.pk}" data-status="{code}">{bullet}{name}</a>'
            )

        menu_items = "".join(options_html)

        return format_html(
            '<div class="order-status-wrapper" id="order-status-wrapper-{}">'
            '  <button type="button" class="order-status-pill-btn" style="background:{};color:{};border:1.5px solid {};" title="Click to change status" data-order-id="{}">'
            '    <span class="status-icon">{}</span>'
            '    <span class="status-name">{}</span>'
            '    <span class="status-chevron">▾</span>'
            '  </button>'
            '  <div class="order-status-popover">'
            '    <div class="popover-header">Update Delivery Status</div>'
            '    {}'
            '  </div>'
            '</div>',
            obj.pk, bg, text, border, obj.pk, icon, label, mark_safe(menu_items)
        )
    status_badge.short_description = "Status"
    status_badge.admin_order_field = "status"

    def delivery_quick_action(self, obj):
        next_actions = {
            'pending': ('confirmed', '👉 Confirm', 'btn-step-confirm', 'Confirm and prepare order'),
            'confirmed': ('out_for_delivery', '🚚 Dispatch', 'btn-step-dispatch', 'Hand over to delivery partner'),
            'out_for_delivery': ('delivered', '✓ Mark Delivered', 'btn-step-delivered', 'Mark order successfully delivered'),
            'delivered': (None, '✓ Delivered', 'btn-step-complete', 'Order fulfilled'),
            'cancelled': ('pending', '↺ Reopen', 'btn-step-reopen', 'Reopen cancelled order'),
        }
        target_status, label, css_class, title = next_actions.get(
            obj.status, (None, '-', 'btn-step-complete', '')
        )

        if target_status:
            url = reverse('admin:store_order_quick_status', args=[obj.pk, target_status])
            return format_html(
                '<a href="{}" class="order-step-btn {}" title="{}" data-order-id="{}" data-target-status="{}">'
                '  <span>{}</span>'
                '</a>',
                url, css_class, title, obj.pk, target_status, label
            )
        else:
            return format_html(
                '<span class="order-step-btn {}">{}</span>',
                css_class, label
            )
    delivery_quick_action.short_description = "Quick Action"

    def delivery_pipeline_status(self, obj):
        if not obj.pk:
            return '-'
        stages = [
            ('pending', 'Pending', '⏳'),
            ('confirmed', 'Confirmed', '📋'),
            ('out_for_delivery', 'Out for Delivery', '🚚'),
            ('delivered', 'Delivered', '📦'),
        ]
        status_order = ['pending', 'confirmed', 'out_for_delivery', 'delivered']
        current_idx = status_order.index(obj.status) if obj.status in status_order else -1
        is_cancelled = (obj.status == 'cancelled')

        html = ['<div class="delivery-pipeline-tracker">']
        for idx, (code, title, icon) in enumerate(stages):
            if is_cancelled:
                step_class = "pipeline-step cancelled"
            elif current_idx >= idx:
                step_class = "pipeline-step completed" if current_idx > idx else "pipeline-step active"
            else:
                step_class = "pipeline-step pending"
            
            quick_url = reverse('admin:store_order_quick_status', args=[obj.pk, code])
            html.append(
                f'<a href="{quick_url}" class="{step_class}" title="Click to set status to {title}">'
                f'  <span class="step-icon">{icon}</span>'
                f'  <span class="step-title">{title}</span>'
                f'</a>'
            )
            if idx < len(stages) - 1:
                html.append('<span class="pipeline-connector">➔</span>')

        if is_cancelled:
            reopen_url = reverse('admin:store_order_quick_status', args=[obj.pk, 'pending'])
            html.append('<span class="pipeline-cancelled-tag">❌ Order Cancelled</span>')
            html.append(f'<a href="{reopen_url}" class="pipeline-reopen-btn">↺ Reopen Order</a>')
        else:
            cancel_url = reverse('admin:store_order_quick_status', args=[obj.pk, 'cancelled'])
            html.append(f'<a href="{cancel_url}" class="pipeline-cancel-btn" title="Cancel this order">✕ Cancel Order</a>')

        html.append('</div>')
        return mark_safe("".join(html))
    delivery_pipeline_status.short_description = "Live Delivery Pipeline"

    def order_actions(self, obj):
        edit_url = reverse('admin:store_order_change', args=[obj.pk])
        return format_html(
            '<div class="admin-row-actions">'
            '  <a href="{}" class="action-btn edit-btn" title="View/Edit Order Details">👁️ View Order</a>'
            '</div>',
            edit_url
        )
    order_actions.short_description = "Actions"



