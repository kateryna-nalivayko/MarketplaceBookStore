from django.db import models
from django.db.models.functions import Now

from books.models import Book
from customer.models import Customer

class OrderItemQueryset(models.QuerySet):

    def total_price(self):
        return sum(cart.products_price() for cart in self)
    
    def total_quantity(self):
        if self:
            return sum(cart.quantity for cart in self)



class Order(models.Model):
    buyer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Покупатель")
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now(), verbose_name="Дата створення замовлення")
    status = models.CharField(max_length=50, default='In Process', verbose_name="Статус заказа")
    notes = models.TextField(blank=True, null=True, verbose_name="Order Notes")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Номер телефону")
    requires_delivery = models.BooleanField(default=False, verbose_name="Потрібна доставка")
    delivery_address = models.TextField(null=True, blank=True, verbose_name="Адреса доставки")
    payment_on_get = models.BooleanField(default=False, verbose_name="Оплата при отримані")
    is_paid = models.BooleanField(default=False, verbose_name="Оплачено")

    class Meta:
        db_table = "order"
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"


    def __str__(self):
        return f"Замовлення № {self.pk} | Покупець {self.buyer.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name="Замовлення", on_delete=models.CASCADE)
    product = models.ForeignKey(Book, verbose_name="Книга", on_delete=models.SET_DEFAULT, default=None)
    name = models.CharField(max_length=150, verbose_name='Назва')
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Ціна')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Кількість')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата продажу")

    class Meta:
        db_table = "order_item"
        verbose_name = "Продана книга"
        verbose_name_plural = "Продані книги"


    objects = OrderItemQueryset.as_manager()

    def products_price(self):
        return round(self.price.amount * self.quantity, 2)

    def __str__(self):
        return f"Товар {self.name} | Заказ {self.order.pk}"