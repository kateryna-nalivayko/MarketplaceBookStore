from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from customer.models import Customer
from orders.models import Order, OrderItem


@login_required
def customer_profile(request):
    if request.user.groups.filter(name='Customer').exists():
        customer = get_object_or_404(Customer, user=request.user)


        context = {
            'customer': customer,
            'user': request.user
        }

        return render(request, 'customer/customer-profile.html', context)


@login_required
def customer_orders(request):
    customer = get_object_or_404(Customer, user=request.user)
    orders = Order.objects.filter(buyer=customer)\
        .prefetch_related("orderitem_set__product__store")
    
    context = {
        "title": 'Замовлення покупців',
        "orders": orders,
        "customer": customer
    }

    return render(request, "customer/customer_orders.html", context)


class CustomerOrdersDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "customer/customer_orders_books_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return Order.objects.filter(buyer=customer)\
            .prefetch_related("orderitem_set__product__store")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = self.object.orderitem_set.all()
        return context
