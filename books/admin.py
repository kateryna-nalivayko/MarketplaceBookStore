from django.contrib import admin
from books.models import Publisher, Author, Book, Genre

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'position', 'parent')
    list_editable = ["position",]
    search_fields = ('name', 'slug')
    list_filter = ('parent',)
