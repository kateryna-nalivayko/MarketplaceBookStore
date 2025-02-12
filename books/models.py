from tkinter import CASCADE
from django.db import models
from django.utils.translation import gettext_lazy as _

from tree_queries.models import TreeNode
from cities_light.models import Country, Region, City
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField

from books.choices import BookStatusChoices, DeliverChoices
from store.models import Store

from model_utils.fields import StatusField, MonitorField
from model_utils import Choices




class Genre(TreeNode):
    name = models.CharField(max_length=150, unique=True, verbose_name="Жанр")
    slug = models.SlugField(
        max_length=200, unique=True, blank=True, null=True, verbose_name="URL"
    )
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "genre"
        verbose_name = "Жанр"
        verbose_name_plural = "Жанри"

        ordering = ["position"]

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Автор')
    age = models.CharField(max_length=300)

    class Meta:
        db_table = 'author'
        verbose_name = 'Автор'
        verbose_name_plural = 'Автори'
        ordering = ['name']

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=150, unique=True, db_default='Unknown Publisher', verbose_name='Видавець')

    class Meta:
        db_table = 'publisher'
        verbose_name = 'Видавець'
        verbose_name_plural = 'Видавці'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    STATUS = Choices(
        ('draft', 'Draft'),
        ('pending', 'Pending Confirmation'),
        ('active', 'Active'),
        ('unactive', 'Inactive'),
        ('rejected', 'Rejected')
    )
    LANGUAGE_CHOICES = [
        ("EN", "English"),
        ("UK", "Ukrainian"),
        ("RU", "Russian"),
        ("FR", "French"),
        ("DE", "German"),
    ]
    title = models.CharField(max_length=150, unique=True, verbose_name="Назва книги")
    slug = models.SlugField(
        max_length=200, unique=True, blank=True, null=True, verbose_name="URL"
    )
    quantity = models.PositiveIntegerField(db_default=1, verbose_name="Quantity")
    published_year = models.PositiveBigIntegerField( verbose_name="Рік видання")
    language = models.CharField(
        max_length=2, choices=LANGUAGE_CHOICES, verbose_name="Мова"
    )
    number_of_pages = models.PositiveBigIntegerField(
        null=True, blank=True, verbose_name="Кількість сторінок"
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Опис",
        help_text="Детальний опис книги"
    )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    genre = models.ForeignKey(Genre, verbose_name="Жанр", on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=True, blank=True)
    authors = models.ManyToManyField(Author)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True, null=True)
    status = StatusField(choices_name='STATUS', default='pending')

    class Meta:
        db_table = "book"
        verbose_name = "книга"
        verbose_name_plural = "Книги"
        ordering = ("id",)

    def __str__(self):
        return self.title

    def display_id(self):
        return f"{self.id:05}"


class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to="book_images", blank=True, verbose_name="Зображення"
    )

    class Meta:
        db_table = "book_images"

class DEliveryOption(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='delivery_options')
    delivery_option = models.CharField(max_length=20, choices=DeliverChoices, default=DeliverChoices.PICK_UP)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='Країна')
    region = ChainedForeignKey(
        Region,
        chained_field='country',
        chained_model_field='country',
        blank=True,
        null=True,
        verbose_name='Region (Single)',
        related_name='deliveryoption_single'
    )
    city = ChainedForeignKey(
        City,
        chained_field='region',
        chained_model_field='region',
        blank=True,
        null=True,
        verbose_name='City (Single)',
        related_name='deliveryoption_city'
    )
    region_multiple = ChainedManyToManyField(
        Region,
        chained_field='country',
        chained_model_field='country',
        blank=True,
        verbose_name='Region (Multiple)',
        related_name='deliveryoption_multiple'
    )
    city_multiple = ChainedManyToManyField(
        City,
        chained_field='region_multiple',
        chained_model_field='region',
        blank=True,
        verbose_name='City (Multiple)',
        related_name='deliveryoption_multiple_city'
    )

    class Meta:
        db_table = 'delivery_option'
        verbose_name = 'Варіант доставки'
        verbose_name_plural = 'Варіанти доставки'
    


