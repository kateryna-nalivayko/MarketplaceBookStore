from django.shortcuts import render



def index(request):

    context = {
        'title': 'Книги - головна',
        'bodyh1': 'Маркетплейс книжок',
        'bodyp': 'Все ще в розробцi',
    }
    return render(request, 'main/index.html', context)