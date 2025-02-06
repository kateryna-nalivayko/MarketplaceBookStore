
from fileinput import FileInput
from django.forms import BaseInlineFormSet, CharField, FileField, ImageField, ModelChoiceField, ModelForm, ModelMultipleChoiceField, Textarea, ValidationError, forms, inlineformset_factory

from books.choices import DeliverChoices
from books.models import Author, Book, BookImage, DEliveryOption, Publisher
from store.models import Store


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


class ChangeStoreForm(ModelForm):
    class Meta:
        model = Store
        fields = ('name', 'description', 'image')

        name = CharField(label='Назва магазину', required=True)
        description = CharField(label="Опис магазинн", widget=Textarea, required=True)
        image = ImageField(label='Додайте вашого аватара')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Store.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Магазин з такою назвою вже є")
        return name

class CSVUploadForm(forms.Form):
    csv_file = FileField(label="Upload CSV File")
