from django.urls import path

from customer import views

app_name='customer'

urlpatterns = [
    path('profile/', views.customer_profile, name='customer_profile'),
    path('customer-orders/', views.customer_orders, name="customer_orders"),
    path('orders/<int:pk>/', views.CustomerOrdersDetailView.as_view(), name='customer_orders_details'),
    
]
