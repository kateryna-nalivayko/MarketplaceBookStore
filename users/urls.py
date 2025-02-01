from django.urls import path

from users import views

app_name='users'

urlpatterns = [
    path('verification-pending/', views.verification_pending, name='verification_pending'),
    path('login/', views.sign_in, name='login'),
    path('customer-sign-up/', views.customer_signup_view, name='customer_signup_view'),
    path('logout/', views.logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
]
