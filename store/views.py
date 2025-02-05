from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from store.forms import AddBookForm, BookImageFormSet, DeliveryOptionMultiFormSet
from store.models import Store


@login_required
def store_dash(request):
    if request.user.groups.filter(name='Store').exists():

        store = request.user.store

        context = {
            'store': store
        }

        return render(request, 'store/store-profile.html', context)
    

@login_required
def add_books(request):
    store = get_object_or_404(Store, user=request.user)
    if request.method == "POST":
        book_form = AddBookForm(request.POST)
        image_formset = BookImageFormSet(request.POST, request.FILES)
        delivery_multi_formset = DeliveryOptionMultiFormSet(request.POST)

        if book_form.is_valid() and image_formset.is_valid() \
        and delivery_multi_formset.is_valid():
            try:
                with transaction.atomic():
                    book = _save_book_and_formset(
                        book_form,
                        store,
                        image_formset,
                        delivery_multi_formset
                    )
                return redirect("store:store_dash")
            except Exception as e:
                print('An error occurred:', e)
        else:
            print('Book form errors', book_form.errors)
            print('Image errors', image_formset.errors)
    else:
        book_form = AddBookForm()
        image_formset = BookImageFormSet()
        delivery_multi_formset = DeliveryOptionMultiFormSet()

    context = {
        'book_form': book_form,
        'image_formset': image_formset,
        'delivery_multi_formset': delivery_multi_formset
    }
    return render(request, 'store/add-books.html', context)

def _save_book_and_formset(book_form, store, image_formset, delivery_multi_formset):
    book = book_form.save(commit=False)
    book.store = store
    book.save()

    book_form.save_m2m()

    image_formset.instance = book
    image_formset.save()

    delivery_multi_formset.instance = book
    delivery_multi_formset.save()
    return book