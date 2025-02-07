from django.contrib import admin

from carts.models import Cart

class CartTabAdmin(admin.TabularInline):
    model = Cart
    fields = "book", 'quantity', "created_at"
    search_fields = "book", "quantity", "created_at"
    readonly_fields = ("created_at",)
    extra = 1


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user_display", "book_display", "quantity", "created_at"]
    # list_filter = ["created_at", 'user', "book__name",]       

    def book_display(self, obj):
        return str(obj.book.name)             
                
    def user_display(self, obj):
        if obj.user:
            return str(obj.user)
        return "Анонімний покупець"