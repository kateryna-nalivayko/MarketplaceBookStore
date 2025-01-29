from tabnanny import verbose
from django.db import models
from tree_queries.models import TreeNode

# Create your models here.


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


class Book(models.Model):
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
    author = models.CharField(max_length=150, verbose_name="Автор")
    quantity = models.PositiveIntegerField(db_default=1, verbose_name="Quantity")
    published_year = models.PositiveBigIntegerField( verbose_name="Рік видання")
    language = models.CharField(
        max_length=2, choices=LANGUAGE_CHOICES, verbose_name="Мова"
    )
    number_of_pages = models.PositiveBigIntegerField(
        null=True, blank=True, verbose_name="Кількість сторінок"
    )
    description = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Опис"
    )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    genre = models.ForeignKey(Genre, verbose_name="Жанр", on_delete=models.CASCADE)

    class Meta:
        db_table = "book"
        verbose_name = "книга"
        verbose_name_plural = "Книги"
        ordering = ("id",)

    def __str__(self):
        return self.title


class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to="book_images", blank=True, verbose_name="Зображення"
    )

    class Meta:
        db_table = "book_images"
