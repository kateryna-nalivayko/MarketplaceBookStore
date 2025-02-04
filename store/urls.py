
from django.urls import path

from store.views import add_books, store_dash


app_name='store'

urlpatterns = [
    path('store-dash/', store_dash, name='store_dash'),
    path('add-books/', add_books, name='add_books')
]
