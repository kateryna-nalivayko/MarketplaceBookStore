from django.db import models
from django.db.models import CASCADE

from users.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE)
    image = models.ImageField(upload_to='store_images/', blank=True)
    balance_uah = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer'
        verbose_name = 'Покупець'
        verbose_name_plural = 'Покупці'
        ordering = ['-created_at']