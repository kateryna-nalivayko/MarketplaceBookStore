from django.shortcuts import render
from django.views.generic import TemplateView

from main.models import AboutUs



def index(request):

    context = {
        'title': 'Книги - головна',
        'bodyh1': 'Маркетплейс книжок',
        'bodyp': 'Все ще в розробцi',
    }
    return render(request, 'main/index.html', context)


def about(request):
    about_us = AboutUs.objects.get(id=1)

    context = {
        'title': about_us.title,
        'subtitle': about_us.subtitle,
        'body': about_us.body
    }

    return render(request, 'main/about.html', context)