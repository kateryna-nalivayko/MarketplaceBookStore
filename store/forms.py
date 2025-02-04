
from django.forms import ImageField, ModelForm, inlineformset_factory

from books.models import Book, BookImage


class AddBookForm(ModelForm):
    class Meta:
        model = Book
        fields = (
            'genre', 'title', 'slug',
            'quantity', 'description',
            'number_of_pages', 'published_year',
            'language',
            'price'
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