from email import message
import logging
from django.contrib import messages
from django.db import connection, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
import requests
from django.utils.text import slugify

from books.choices import BookStatusChoices, DeliverChoices
from books.models import Author, Book, BookImage, Genre, Publisher
from orders.models import OrderItem
from store.forms import AddBookForm, BookImageFormSet, CSVUploadForm, ChangeStoreForm, DeliveryOptionMultiFormSet
from store.models import Store

import pandas as pd
from django.core.files.base import ContentFile


import matplotlib
matplotlib.use('Agg')
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
def export_sold_books_excel(request):  
    store = get_object_or_404(Store, user=request.user)

    sold_items = OrderItem.objects.filter(
        product__store=store
    ).select_related("order", "product", "order__buyer")

    data = []
    for item in sold_items:

        buyer_username = (item.order.buyer.user.username 
                        if item.order.buyer and item.order.buyer.user 
                        else "Unknown")
        

        order_date = item.order.created_at.strftime("%Y-%m-%d %H:%M")
        created_at = item.created_at.strftime("%Y-%m-%d %H:%M")

        data.append({
            "Book Name": item.product.title,
            "Quantity": item.quantity,
            "Price": float(item.price), 
            "Total Amount": float(item.price * item.quantity),
            "Buyer": buyer_username,
            "Order Date": order_date,
            "Sale Date": created_at,
            "Payment Status": "Paid" if item.order.is_paid else "Pending",
            "Delivery Address": item.order.delivery_address or "N/A",
            "Phone": item.order.phone_number or "N/A"
        })

    df = pd.DataFrame(data)


    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="sold_books.xlsx"'
    

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sold Books')
        

        workbook = writer.book
        worksheet = writer.sheets['Sold Books']
        

        for idx, column in enumerate(worksheet.columns, 1):
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

    return response


@login_required
def sold_books_analytics(request):
    store = get_object_or_404(Store, user=request.user)
    logger.info(f"Fetching sold items for store: {store}")

    sold_items = OrderItem.objects.filter(
        product__store=store
    ).select_related("order", "product")


    product_names = [item.product.title for item in sold_items]
    quantities = [item.quantity for item in sold_items]
    prices = [item.price for item in sold_items]
    order_dates = [item.order.created_at for item in sold_items]

    logger.info(f"Prepared data for {len(sold_items)} sold items")


    df = pd.DataFrame({
        'Product Name': product_names,
        'Quantity': quantities,
        'Price': prices,
        'Order Date': order_dates
    })
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df.set_index('Order Date', inplace=True)


    plots = []

    try:

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
        logger.info("Generated bar plot for quantities")


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
        logger.info("Generated bar plot for prices")


        plt.figure(figsize=(10, 5))
        df['Quantity'].resample('H').sum().plot(kind='line', color='red')
        plt.xlabel('Order Date')
        plt.ylabel('Total Quantities Sold')
        plt.title('Quantities Sold Over Time (Hourly)')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        plots.append(uri)
        plt.close()
        logger.info("Generated time series plot for quantities sold over time (hourly)")

    except Exception as e:
        logger.error(f"Error generating plots: {e}")
        messages.error(request, f"Error generating plots: {e}")

    context = {
        'plots': plots,
        'store': store
    }

    return render(request, 'store/sold_books_analytics.html', context)


from cities_light.models import Country, Region, City
from books.models import DEliveryOption
logger = logging.getLogger(__name__)
import pandas as pd


@login_required
def import_books_from_csv(request):
    store = get_object_or_404(Store, user=request.user)

    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            xlsx_file = request.FILES["csv_file"]
            
            try:
                df = pd.read_excel(xlsx_file, engine='openpyxl')
                
                with transaction.atomic():
                    for _, row in df.iterrows():

                        product, authors = create_product_from_row(row, store)
                        if product:
                            product.save()
                            
                            
                            if authors:
                                product.authors.set(authors)
                            

                            delivery_option = create_delivery_option(row, product)
                            if delivery_option:
                                delivery_option.save()
                                

                                regions = get_multiple_regions(row.get("multiple_regions", ""), delivery_option.country)
                                if regions:
                                    delivery_option.region_multiple.set(regions)
                                
                                cities = get_multiple_cities(row.get("multiple_cities", ""), regions)
                                if cities:
                                    delivery_option.city_multiple.set(cities)


                            image = create_book_image(row, product)
                            if image:
                                image.save()

                messages.success(request, "Файл з книгами іспішно доданий!")
                return redirect("store:book_list")

            except Exception as e:
                logger.error(f"Error importing products: {e}")
                messages.error(request, f"Error importing products: {e}")
                transaction.rollback()

    else:
        form = CSVUploadForm()

    return render(request, "store/import_books.html", {"form": form})

def reset_sequence(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), coalesce(max(id), 1), max(id) IS NOT null) FROM {table_name};")



def create_product_from_row(row, store):
    required_fields = ["title", "genre", "country", "price", "published_year", "language"]
    missing_fields = [field for field in required_fields if pd.isna(row.get(field))]
    
    if missing_fields:
        logger.warning(f"Skipping row due to missing fields: {missing_fields} in row: {row}")
        return None

    genre = get_existing_genre(row["genre"])
    country = get_existing_country(row["country"])
    publisher = Publisher.objects.filter(name=row.get("publisher")).first()

    if not genre or not country:
        logger.warning(f"Invalid genre/country: {row}")
        return None


    if row.get("language") not in dict(Book.LANGUAGE_CHOICES):
        logger.warning(f"Invalid language choice: {row.get('language')}")
        return None

    book = Book(
        store=store,
        title=row["title"],
        description=row.get("description", ""),
        price=row["price"],  # Fix: Remove array syntax
        quantity=row.get("quantity", 1),
        genre=genre,  # Fix: Use genre object instead of array
        status=row.get("status", "draft"),
        published_year=row["published_year"],
        language=row["language"],
        number_of_pages=row.get("number_of_pages"),
        publisher=publisher,
        slug=slugify(row["title"])  # Add slug generation
    )

    # Handle authors if provided
    if "authors" in row and row["authors"]:
        author_names = [name.strip() for name in row["authors"].split(',')]
        authors = []
        for author_name in author_names:
            author, created = Author.objects.get_or_create(name=author_name)
            authors.append(author)
        
        # Note: We'll need to set authors after saving the book
        return book, authors

    return book, []



def create_delivery_option(row, product):
    if "delivery_option" not in row or "country" not in row:
        return None

    country = Country.objects.filter(name=row["country"]).first()
    if not country:
        logger.warning(f"Country '{row['country']}' not found")
        return None

    delivery_option = row.get("delivery_option", "").strip().lower()
    if delivery_option not in dict(DeliverChoices.choices).keys():
        logger.warning(f"Invalid delivery option '{delivery_option}'")
        return None

    return DEliveryOption.objects.create(
        book=product,
        delivery_option=delivery_option,
        country=country
    )



def create_book_image(row, product):
    image_url = row.get("image_url")
    if not image_url or not isinstance(image_url, str):
        return None

    try:
        response = requests.get(image_url, timeout=5)
        if response.status_code == 200:
            product_image = BookImage(book=product)
            product_image.image.save(f"{product.title}.jpg", ContentFile(response.content), save=False)
            return product_image
    except requests.RequestException as e:
        logger.warning(f"Could not download image for {product.title}: {e}")  # Changed from product.name to product.title

    return None


def get_existing_genre(name):
    genre = Genre.objects.filter(name=name).first()
    if not genre:
        logger.warning(f"Genre '{name}' not found in the db")  # Changed "not fount" to "not found"
    return genre



def get_existing_country(name):
    country = Country.objects.filter(name=name).first()
    if not country:
        logger.warning(f"Country '{name}' not found in the database.")
    return country


def get_multiple_regions(region_names, country):
    if not region_names:
        return []
    
    regions = []
    for region_name in region_names.split(','):
        region = Region.objects.filter(name=region_name.strip(), country=country).first()
        if region:
            regions.append(region)
        else:
            logger.warning(f"Region '{region_name}' not found in {country}")
    
    return regions

def get_multiple_cities(city_names, regions):
    if not city_names or not regions:
        return []
    
    cities = []
    for city_name in city_names.split(','):
        city = City.objects.filter(
            name=city_name.strip(),
            region__in=regions
        ).first()
        if city:
            cities.append(city)
        else:
            logger.warning(f"City '{city_name}' not found in given regions")
    
    return cities