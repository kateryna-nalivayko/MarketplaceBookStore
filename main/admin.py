from django.contrib import admin

from main.models import AboutUs


@admin.register(AboutUs)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'subtitle',)