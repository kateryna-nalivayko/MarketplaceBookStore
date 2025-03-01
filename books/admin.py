from django.contrib import admin
from books.models import Publisher, Author, Book, Genre
from django.utils.html import format_html

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'position', 'parent')
    list_editable = ["position",]
    search_fields = ('name', 'slug')
    list_filter = ('parent',)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'age')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_year', 'language', 'price', 'quantity', 'get_status')
    search_fields = ('title', 'authors__name', 'publisher__name')
    list_filter = ('language', 'genre', 'publisher', 'status')
    filter_horizontal = ('authors',)

    def get_status(self, obj):
        status_colors = {
            'draft': '#6c757d',      # gray
            'pending': '#ffc107',     # yellow
            'active': '#28a745',      # green
            'unactive': '#dc3545',    # red
            'rejected': '#dc3545'     # red
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status.short_description = 'Status'
    get_status.admin_order_field = 'status'

