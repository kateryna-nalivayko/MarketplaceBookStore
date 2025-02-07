from django.db import models

from books.models import Book
from users.models import User


class CartQueryset(models.QuerySet):

    def total_price(self):
        return sum(cart.products_price() for cart in self)
    
    def total_quantity(self):
        if self:
            return sum(cart.quantity for cart in self)
        return 0


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Покупець')
    product = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Кількість')
    session_key = models.CharField(blank=True, null=True, max_length=32)
    created_at = models.DateField(auto_now=True, verbose_name='Дата додавання')

    class Meta:
        db_table = 'cart'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзини'
    
    objects = CartQueryset().as_manager()

    def products_price(self):
        return round(self.product.price * self.quantity, 2)
    
    def __str__(self):
        if self.user:
            return f'Корзина {self.user.username} | Книга {self.product.name} | Кількість - {self.quantity}'
        return f'Анонімна корзина | Книга {self.product.name} | Кількість - {self.quantity}'