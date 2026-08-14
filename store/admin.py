from django.contrib import admin

from .models import Category, Order, OrderItem, Product, StoreConfig


@admin.register(StoreConfig)
class StoreConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not StoreConfig.objects.exists()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'phone', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('order_number', 'customer_latitude', 'customer_longitude', 'distance_km')
    inlines = [OrderItemInline]
