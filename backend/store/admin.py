from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'unit', 'is_available', 'updated_at')
    list_filter = ('category', 'is_available', 'created_at')
    list_editable = ('price', 'is_available')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
