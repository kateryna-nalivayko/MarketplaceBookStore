from django.contrib import admin

from users.models import User


@admin.register(User)
class UserADmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'email',]
    search_fields = ['username', 'first_name', 'email',]