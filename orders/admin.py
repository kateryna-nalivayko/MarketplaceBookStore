from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('product', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'created_at', 'status', 'total_price')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__name', 'status')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('buyer', 'status', 'total_amount', 'notes')
        }),
        ('Dates', {
            'fields': ('created_at',),
        }),
    )

    def total_price(self, obj):
        return obj.orderitem_set.all().total_price()
    total_price.short_description = 'Total Price'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    list_filter = ('order__status', 'product')
    search_fields = ('order__buyer__name', 'product__name')
    ordering = ('-order__created_at',)
    readonly_fields = ('order', 'product', 'quantity', 'price')
    fieldsets = (
        (None, {
            'fields': ('order', 'product', 'quantity', 'price')
        }),
    )