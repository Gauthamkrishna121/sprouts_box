from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Category, Product

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

