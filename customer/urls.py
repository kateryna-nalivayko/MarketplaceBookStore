from django.urls import path

from customer import views

app_name='customer'

urlpatterns = [
    path('profile/', views.customer_profile, name='customer_profile')
]
