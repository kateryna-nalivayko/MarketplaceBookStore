from django import forms

from books.models import DEliveryOption


class DeliveryOptionCatalogForm(forms.ModelForm):
    class Meta:
        model = DEliveryOption
        fields = ['delivery_option', 'country', 'region', 'city']

    def __init__(self, *args, **kwargs):
        book = kwargs.pop('product', None)  # Get the product from kwargs
        super().__init__(*args, **kwargs)

        if book:
            # Set initial values based on the product if needed
            self.fields['delivery_option'].initial = book.delivery_options.first().delivery_option if book.delivery_options.exists() else None
            # Set other initial fields if necessary based on the product
