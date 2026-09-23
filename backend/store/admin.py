from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

    def product_count(self, obj):
        count = obj.products.count()
        return format_html('<span style="background: #e8f3ec; color: #1b4332; font-weight: 600; padding: 3px 10px; border-radius: 12px; font-size: 0.85rem;">{} products</span>', count)
    product_count.short_description = "Total Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_thumbnail', 'name', 'category', 'formatted_price', 'unit', 'availability_badge', 'updated_at')
    list_filter = ('category', 'is_available', 'created_at')
    list_editable = ('is_available',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_per_page = 20

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 8px; border: 1px solid #ece8df;" />', obj.image.url)
        return format_html('<div style="width: 45px; height: 45px; background: #e8f3ec; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #1b4332; font-weight: bold; font-size: 0.8rem;">📦</div>')
    image_thumbnail.short_description = "Image"

    def formatted_price(self, obj):
        return format_html('<span style="font-weight: 700; color: #132a1c;">₹{}</span>', obj.price)
    formatted_price.short_description = "Price"

    def availability_badge(self, obj):
        if obj.is_available:
            return format_html('<span style="background: #d4edda; color: #155724; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.8rem;">In Stock</span>')
        return format_html('<span style="background: #f8d7da; color: #721c24; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.8rem;">Out of Stock</span>')
    availability_badge.short_description = "Status"
