from django.urls import path

from store import views


app_name='store'

urlpatterns = [
    path('store-dash/', views.store_dash, name='store_dash'),
    path('add-books/', views.add_books, name='add_books'),

    path('books-list', views.BaseBookListView.as_view(), name='book_list'),
    path('books/active/', views.ActiveBookListView.as_view(), name='active_books'),
    path('books/pending/', views.PendingBooktListView.as_view(), name='pending_books'),
    path('books/inactive/', views.InactiveBookListView.as_view(), name='inactive_books'),
    path('books/rejected/', views.RejectedBooktListView.as_view(), name='rejected_books'),

    path('books/deactivate/', views.deactivate_books, name='deactivate_books'),
    path('books/activate/', views.activate_books, name='activate_books'),

    path('change-store/', views.change_store, name='change_store'),

    path("export-books/", views.export_books_to_csv, name="export_books"),
]
