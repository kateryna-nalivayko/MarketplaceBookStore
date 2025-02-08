from email import message
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView

from books.choices import BookStatusChoices
from books.models import Book
from orders.models import OrderItem
from store.forms import AddBookForm, BookImageFormSet, CSVUploadForm, ChangeStoreForm, DeliveryOptionMultiFormSet
from store.models import Store

import pandas as pd

from store.utils import process_csv

import matplotlib.pyplot as plt
import io
import urllib, base64


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
    book.status = 'pending'
    book.save()

    book_form.save_m2m()

    image_formset.instance = book
    image_formset.save()

    delivery_multi_formset.instance = book
    delivery_multi_formset.save()
    return book


@method_decorator(login_required, name='dispatch')
class BaseBookListView(ListView):
    model = Book
    template_name = 'store/book-list.html'
    context_object_name = 'books'

    def get_queryset(self):
        store = get_object_or_404(Store, user=self.request.user)

        return Book.objects.filter(store=store).prefetch_related(
            "delivery_options__region_multiple",
            "delivery_options__city_multiple"
        )

class ActiveBookListView(BaseBookListView):
    def get_queryset(self):
        queryset =  super().get_queryset()
        return queryset.filter(status='active')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_type'] = 'active'
        return context


class InactiveBookListView(BaseBookListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status='unactive')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_type'] = 'inactive'
        return context
    
class PendingBooktListView(BaseBookListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status='pending')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_type'] = 'pending'
        return context


class RejectedBooktListView(BaseBookListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status='rejected')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_type'] = 'rejected'
        return context

@login_required
def deactivate_books(request):
    if request.method == 'POST':
        book_ids = request.POST.getlist('book_ids')
        if book_ids:
            books = Book.objects.filter(id__in=book_ids,
                                        store=request.user.store,
                                        status=BookStatusChoices.ACTIVE)
            books.update(status='unactive')
        else:
            print('Error to status')
    return redirect('store:book_list')


@login_required
def activate_books(request):
    if request.method == 'POST':
        book_ids = request.POST.getlist('book_ids')
        if book_ids:
            books = Book.objects.filter(id__in=book_ids,
                                        store=request.user.store,
                                        status='unactive')
            books.update(status='active')
        else:
            print('Error to status')
    return redirect('store:book_list')

@login_required
def change_store(request):
    store = Store.objects.get(user=request.user)

    if request.method == "POST":
        form = ChangeStoreForm(instance=store, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('store:store_dash'))
    else:
        form = ChangeStoreForm()
    context = {
            'title': 'Change Store',
            'form': form
        }
    return render(request, 'store/change_store_form.html', context)


@login_required
def export_books_to_csv(request):
    store = get_object_or_404(Store, user=request.user)
    books = get_books_with_related_data(store)
    data = prepare_books_data(books)
    response = create_csv_response(data)
    return response

def get_books_with_related_data(store):
    return Book.objects.filter(store=store).prefetch_related(
        "authors", "genre", "publisher", 
        "delivery_options__region_multiple", 
        "delivery_options__city_multiple"
    )

def prepare_books_data(books):
    data = []
    for book in books:
        data.append({
            "Title": book.title,
            "Author(s)": get_authors(book),
            "Genre": book.genre.name if book.genre else "",
            "Publisher": book.publisher.name if book.publisher else "Unknown",
            "Published Year": book.published_year,
            "Language": dict(Book.LANGUAGE_CHOICES).get(book.language, book.language),
            "Pages": book.number_of_pages or "N/A",
            "Quantity": book.quantity,
            "Price (USD)": book.price,
            "Status": book.get_status_display(),
            "Delivery Options": get_delivery_options(book),
            "Delivery Regions": get_delivery_regions(book),
            "Delivery Cities": get_delivery_cities(book),
            "Delivery Countries": get_delivery_countries(book),
            "Created At": book.created_at.strftime("%Y-%m-%d"),
            "Updated At": book.updated_at.strftime("%Y-%m-%d"),
        })
    return data

def get_authors(book):
    return ", ".join([author.name for author in book.authors.all()])

def get_delivery_options(book):
    return ", ".join([option.get_delivery_option_display() for option in book.delivery_options.all()])

def get_delivery_regions(book):
    return ", ".join([region.name for option in book.delivery_options.all() for region in option.region_multiple.all()])

def get_delivery_cities(book):
    return ", ".join([city.name for option in book.delivery_options.all() for city in option.city_multiple.all()])

def get_delivery_countries(book):
    return ", ".join([option.country.name for option in book.delivery_options.all()])

def create_csv_response(data):
    df = pd.DataFrame(data)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="books_export.csv"'
    df.to_csv(response, index=False, encoding='utf-8-sig', sep=',')
    return response


@login_required
def sold_books_view(request):
    store = get_object_or_404(Store, user=request.user)

    sold_items = OrderItem.objects.filter(
        product__store=store
    ).select_related("order", "product", "order__buyer")

    context = {
        "sold_items": sold_items,
        "store": store
    }

    return render(request, "store/sold_books.html", context)


class SoldBooksDetailView(LoginRequiredMixin, DetailView):
    model = OrderItem
    template_name = "store/sold_books_detail.html"
    context_object_name = "sold_item"

    def get_queryset(self):
        store = get_object_or_404(Store, user=self.request.user)
        return OrderItem.objects.filter(product__store=store).select_related('order', 'product')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["store"] = get_object_or_404(Store, user=self.request.user)
        context['phone_number'] = self.object.order.phone_number
        context['delivery_address'] = self.object.order.delivery_address
        context['is_paid'] = self.object.order.is_paid
        context['total_amount'] = self.object.order.total_amount
        return context


@login_required
def export_sold_books_csv(request):
    store = get_object_or_404(Store, user=request.user)

    sold_items = OrderItem.objects.filter(
        product__store=store
    ).select_related("order", "product", "order__buyer")

    data = []
    for item in sold_items:
        buyer_username = item.order.buyer.user.username if item.order.buyer and item.order.buyer.user else "Unknown"
        data.append({
            "Product Name": item.product.title,
            "Quantity": item.quantity,
            "Price": item.price,
            "Buyer": buyer_username,
            "Order Date": item.order.created_at,
        })

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sold_books.csv"'
    df.to_csv(path_or_buf=response, index=False)

    return response


@login_required
def sold_books_analytics(request):
    store = get_object_or_404(Store, user=request.user)

    sold_items = OrderItem.objects.filter(
        product__store=store
    ).select_related("order", "product")

    # Data preparation
    product_names = [item.product.title for item in sold_items]
    quantities = [item.quantity for item in sold_items]
    prices = [item.price for item in sold_items]
    order_dates = [item.order.created_at for item in sold_items]

    # Create a DataFrame for time series analysis
    df = pd.DataFrame({
        'Product Name': product_names,
        'Quantity': quantities,
        'Price': prices,
        'Order Date': order_dates
    })
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df.set_index('Order Date', inplace=True)

    # Plotting
    plots = []

    # Bar plot for quantities
    plt.figure(figsize=(10, 5))
    plt.bar(product_names, quantities, color='blue')
    plt.xlabel('Product Names')
    plt.ylabel('Quantities Sold')
    plt.title('Quantities of Sold Books')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plots.append(uri)
    plt.close()

    # Bar plot for prices
    plt.figure(figsize=(10, 5))
    plt.bar(product_names, prices, color='green')
    plt.xlabel('Product Names')
    plt.ylabel('Prices')
    plt.title('Prices of Sold Books')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plots.append(uri)
    plt.close()

    # Time series plot for quantities sold over time (daily)
    plt.figure(figsize=(10, 5))
    df['Quantity'].resample('D').sum().plot(kind='line', color='red')
    plt.xlabel('Order Date')
    plt.ylabel('Total Quantities Sold')
    plt.title('Quantities Sold Over Time (Daily)')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plots.append(uri)
    plt.close()

    context = {
        'plots': plots,
        'store': store
    }

    return render(request, 'store/sold_books_analytics.html', context)