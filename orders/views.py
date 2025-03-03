from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.forms import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView

from carts.models import Cart

from orders.forms import CreateOrderForm
from orders.models import Order, OrderItem

class CreateOrderView(LoginRequiredMixin, FormView):
    template_name = 'orders/create_order.html'
    form_class = CreateOrderForm
    success_url = reverse_lazy('main:index')

    def get_initial(self):
        initial = super().get_initial()
        initial['first_name'] = self.request.user.first_name
        initial['last_name'] = self.request.user.last_name
        return initial

    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = self.request.user
                cart_items = Cart.objects.filter(user=user)

                if cart_items.exists():
                    order = Order.objects.create(
                        buyer=user.customer,
                        phone_number=form.cleaned_data['phone_number'],
                        requires_delivery=form.cleaned_data['requires_delivery'] == '1',
                        delivery_address=form.cleaned_data['delivery_address'],
                        payment_on_get=form.cleaned_data['payment_on_get'] == '1',
                    )

                    total_amount = 0

                    for cart_item in cart_items:
                        product = cart_item.product
                        name = cart_item.product.title
                        price = cart_item.product.price
                        quantity = cart_item.quantity

                        if product.quantity < quantity:
                            raise ValidationError(f'Недостатня кількість {name} на складу. В наявності - {product.quantity}')

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            name=name,
                            price=price,
                            quantity=quantity,
                        )
                        product.quantity -= quantity
                        product.save()

                        total_amount += price * quantity

                    order.total_amount = total_amount
                    order.save()

                    cart_items.delete()

                    messages.success(self.request, 'Замовлення оформлене!')
                    return redirect('main:index')
        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect('orders:create_order')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Заповніть всі обовʼязкові поля!')
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оформлення замовлення'
        context['order'] = True
        return context