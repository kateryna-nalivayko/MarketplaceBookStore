from django.urls import path

from books import views

app_name = 'books'

urlpatterns = [
    path('<slug:category_slug>/', views.CatalogView.as_view(), name='index'),
    path('book/<slug:product_slug>/', views.book, name='book'),
]