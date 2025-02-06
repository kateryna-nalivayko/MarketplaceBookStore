from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from customer.models import Customer


@login_required
def customer_profile(request):
    if request.user.groups.filter(name='Customer').exists():
        customer = get_object_or_404(Customer, user=request.user)


        context = {
            'customer': customer,
            'user': request.user
        }

        return render(request, 'customer/customer-profile.html', context)

