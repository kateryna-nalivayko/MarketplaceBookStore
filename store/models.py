from django.db.models import CASCADE
import uuid
from django.db import models
from django.utils.text import slugify

from users.models import User


class Store(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE)
    name = models.CharField(max_length=150, unique=True, null=True, verbose_name='Назва магазину')
    slug = models.SlugField(max_length=150, unique=True, null=True)
    description = models.TextField(null=True)
    image = models.ImageField(upload_to='store_images/', blank=True)
    balance_uah = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store'
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазини'
        ordering = ['-created_at']


    def save(self, *args, **kwargs):
        if not self.slug or self.name and self.slug != slugify(self.name):
            base_slug = slugify(self.name)
            unique_slug = base_slug
            count = 1

            while Store.objects.filter(slug=unique_slug).exclude(id=self.id).exists():
                unique_slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
                count += 1

            self.slug = unique_slug
        super(Store, self).save(*args, **kwargs)