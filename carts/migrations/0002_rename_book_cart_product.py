# Generated by Django 5.1.6 on 2025-02-07 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='book',
            new_name='product',
        ),
    ]
