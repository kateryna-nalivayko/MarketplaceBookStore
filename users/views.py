from django.contrib import auth, messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from carts.models import Cart
from customer.models import Customer
from store.models import Store
from users.forms import CustomAuthenticationForm, CustomerSignUpForm, StoreSignUpForm

from verify_email.email_handler import ActivationMailManager


def sign_in(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = auth.authenticate(username=username, password=password)

            session_key = request.session.session_key

            if user:
                auth.login(request, user)
                messages.success(request, f"{username}, Ви увійшли в аккаунт")
                
                if session_key:
                    Cart.objects.filter(session_key=session_key).update(user=user)

                redirect_page = request.POST.get('next', None)
                if redirect_page and redirect_page != reverse('user:logout'):
                    return HttpResponseRedirect(request.POST.get('next'))
                
                return HttpResponseRedirect(reverse('main:index'))
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
        'title': 'Emali = процес верифікації. Успіх'
    }
    return render(request, 'email_templates/email_verification_pending.html', context)


@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse('main:index'))


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            auth.update_session_auth_hash(request, form.user)
            return redirect(reverse('main:index'))
    else:
        form = PasswordChangeForm(user=request.user)
    
    context = {
        'title': 'Зміна паролю',
        'form': form
    }

    return render(request, 'users/change_password.html', context)


def store_signup_view(request):
    if request.method == 'POST':
        form = StoreSignUpForm(request.POST)
            
        if form.is_valid():
            user = None
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()

                    store_group = Group.objects.get(name='Store')
                    user.groups.add(store_group)
                    user.save()
                    user.refresh_from_db()

                    Store.objects.get_or_create(user=user)

                    ActivationMailManager.send_verification_link(
                        inactive_user=user, form=form, request=request
                    )
                    messages.success(request, "Все повний люкс. Реєстрація в процесі")
                    return redirect('user:verification_pending')
            except Exception as e:
                if user and user.pk:
                    user.delete()
        else:
            print('Form errors', form.errors)
    else:
        form = CustomerSignUpForm()


    return render(request, 'users/store_sign_up.html', {'form': form})