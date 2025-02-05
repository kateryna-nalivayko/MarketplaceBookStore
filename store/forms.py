
from django.forms import BaseInlineFormSet, ImageField, ModelChoiceField, ModelForm, ModelMultipleChoiceField, forms, inlineformset_factory

from books.choices import DeliverChoices
from books.models import Author, Book, BookImage, DEliveryOption, Publisher


class AddBookForm(ModelForm):
    authors = ModelMultipleChoiceField(queryset=Author.objects.all(), required=True)
    publisher = ModelChoiceField(queryset=Publisher.objects.all(), required=True)
    class Meta:
        model = Book
        fields = (
            'genre', 'title', 'slug',
            'quantity', 'description',
            'number_of_pages', 'published_year',
            'language',
            'price',
            'authors',
            'publisher'
        )


class BookImageForm(ModelForm):
    class Meta:
        model = BookImage
        fields = ('image', )

        image = ImageField(label='', required=False)

BookImageFormSet = inlineformset_factory(
    Book,
    BookImage,
    form=BookImageForm,
    extra=3,
    can_delete=True,
)

class DeliveryOptionMultiForm(ModelForm):
    class Meta:
        model = DEliveryOption
        fields = ['delivery_option', 'country', 'region_multiple',
                  'city_multiple']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delivery_option'].initial = DeliverChoices.DELIVER


class BaseDeliveryOptionMultiFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

DeliveryOptionMultiFormSet = inlineformset_factory(
    Book,
    DEliveryOption,
    form=DeliveryOptionMultiForm,
    extra=1,
    can_delete=True
)
