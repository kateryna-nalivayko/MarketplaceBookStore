from django.contrib import auth, messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required

from customer.models import Customer
from users.forms import CustomAuthenticationForm, CustomerSignUpForm

from verify_email.email_handler import ActivationMailManager


def sign_in(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = auth.authenticate(username=username, password=password)

            if user:
                auth.login(request, user)
                messages.success(
                    request, "f{username}, Ви успішно увійшли до вашого аккаунту"
                )

            redirect_page = request.POST.get("next", None)
            if redirect_page and redirect_page != reverse("user:logout"):
                return HttpResponseRedirect(request.POST.get("next"))

            return HttpResponseRedirect(reverse("main:index"))
    else:
        form = CustomAuthenticationForm()

    context = {"title": "Book - авторизація", "form": form}
    return render(request, "users/login.html", context)


def customer_signup_view(request):
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = None
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()

                    customer_group = Group.objects.get(name='Customer')
                    user.groups.add(customer_group)
                    user.save()
                    user.refresh_from_db()
                    Customer.objects.get_or_create(user=user)

                    ActivationMailManager.send_verification_link(
                        inactive_user=user, form=form, request=request
                    )
                    messages.success(
                        request,
                        'Ваш аккаунт був успішно створенний. Будь-ласка, підтвердіть ваш email, щоб активувати його'
                    )
                    return redirect('user:verification_pending')
            except Exception as e:
                if user and user.pk:
                    user.delete()
                messages.error(request, f'Помилка під час реєстрації: {e}')
        else:
            print('Form errors:', form.errors)
    else:
        form = CustomerSignUpForm()
    return render(request, 'users/customersignup.html', {'form': form})


def verification_pending(request):
    context = {
        'title': 'Email - процес верифікації. Успіх'
    }
    return render(request, 'email_templates/email_verification_pending.html')


def verification_pending(request):
    context = {
        'title': 'Emali = процес верифікації. Успіх'
    }
    return render(request, 'email_templates/email_verification_pending.html', context)


@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse('main:index'))