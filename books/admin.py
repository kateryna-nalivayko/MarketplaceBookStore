from django.contrib import admin
from books.models import Publisher, Author, Book, Genre

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
    list_display = ('title', 'published_year', 'language', 'price', 'quantity')
    search_fields = ('title', 'authors__name', 'publisher__name')
    list_filter = ('language', 'genre', 'publisher')
    filter_horizontal = ('authors',)

