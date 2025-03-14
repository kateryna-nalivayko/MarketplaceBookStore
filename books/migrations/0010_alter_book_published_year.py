# Generated by Django 5.1.6 on 2025-03-04 07:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0009_alter_book_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='published_year',
            field=models.PositiveBigIntegerField(validators=[django.core.validators.MaxValueValidator(2025, message='Published year cannot be greater than 2025')], verbose_name='Рік видання'),
        ),
    ]
