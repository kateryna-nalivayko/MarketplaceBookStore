from django.shortcuts import render
from django.views.generic import TemplateView



def index(request):

    context = {
        'title': 'Книги - головна',
        'bodyh1': 'Маркетплейс книжок',
        'bodyp': 'Все ще в розробцi',
    }
    return render(request, 'main/index.html', context)


class AboutView(TemplateView):
    template_name = 'main/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Книги - про нас'
        context['h1'] = 'Про нас'
        context['body'] = 'Я - маркетплейс книжок. Я ще в розробцi.'
        return context