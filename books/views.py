import logging
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
import requests
from django.core.files.base import ContentFile


from books.choices import DeliverChoices
from books.forms import DeliveryOptionCatalogForm
from books.models import Book, BookImage, Genre


class CatalogView(ListView):
    model = Book
    template_name = "books/catalog.html"
    context_object_name = "goods"
    paginate_by = 5

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        order_by = self.request.GET.get("order_by")

        # Use select_related for ForeignKey relationships to reduce queries
        queryset = Book.objects.filter(status='active').select_related('genre', 'store').prefetch_related("images", "delivery_options")

        # Filter by category if a category_slug is provided
        if category_slug:
            self.parent_category = get_object_or_404(Genre, slug=category_slug)
            descendants = self.parent_category.descendants(include_self=True)
            queryset = queryset.filter(genre__in=descendants)

        # Apply ordering if provided
        if order_by:
            queryset = queryset.order_by(order_by)
        

        # Apply additional filters like delivery options, region, and city
        queryset = self.apply_filters(queryset)

        return queryset

    def apply_filters(self, queryset):
        # Retrieve filter parameters from the request
        delivery_option = self.request.GET.get("delivery_option")
        country_id = self.request.GET.get("country")

        # Filter by delivery option
        if delivery_option:
            queryset = queryset.filter(delivery_options__delivery_option=delivery_option)



            region_multiple_ids = self.request.GET.getlist("region_multiple")
            city_multiple_ids = self.request.GET.getlist("city_multiple")

            if region_multiple_ids:
                queryset = queryset.filter(delivery_options__region_multiple__in=region_multiple_ids)
            if city_multiple_ids:
                queryset = queryset.filter(delivery_options__city_multiple__in=city_multiple_ids)

        # Filter by country
        if country_id:
            queryset = queryset.filter(delivery_options__country_id=country_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumb_categories"] = self.get_breadcrumbs()
        context["immediate_children"] = self.get_immediate_children()
        context["parent_category"] = self.parent_category
        context["slug_url"] = self.kwargs.get("category_slug")

        # Initialize the form without passing 'product' since it's not in the form's fields
        context["form"] = DeliveryOptionCatalogForm()

        return context

    def get_breadcrumbs(self):
        breadcrumb_categories = []
        if self.parent_category:
            category = self.parent_category
            while category:
                breadcrumb_categories.insert(0, category)
                category = category.parent
        return breadcrumb_categories

    def get_immediate_children(self):
        # Use the pre-fetched parent_category if available
        if self.parent_category:
            return self.parent_category.children.all()
        return Genre.objects.filter(parent=None)


def book(request, product_slug):
    book = get_object_or_404(
        Book.objects.prefetch_related("delivery_options", "images"),
        slug=product_slug,
    )

    category = book.genre
    breadcrumb_categories = []
    while category:
        breadcrumb_categories.insert(0, category)
        category = category.parent

    context = {
        "book": book,
        "delivery_options": book.delivery_options.all(),
        "breadcrumb_categories": breadcrumb_categories,
    }


    return render(request, "books/book.html", context)