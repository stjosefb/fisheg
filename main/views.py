from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader


def index(request):
    #return HttpResponse("Hello, world. You're at the main index.")
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    #output = ', '.join([q.question_text for q in latest_question_list])
    #return HttpResponse(output)
    template = loader.get_template('main/index.html')
    context = {
        'menu_list': [
                {'title': 'Image Management', 'slug': 'image_mng'},
                {'title': 'Data set Management', 'slug': 'data_set_mng'},
            ],
    }
    return HttpResponse(template.render(context, request))