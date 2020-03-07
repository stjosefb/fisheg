from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
import json
import os
from fisheg import settings


def index(request):
    message = ''
    if 'message' in request.GET:
        message = request.GET['message']
    template = loader.get_template('ref_dataset_mng/index.html')
    #subfolders = [f.name for f in os.scandir(settings.BASE_DATASETS_PATH) if f.is_dir()]
    context = {
        #'dataset_list': subfolders,
        'message': message
    }
    return HttpResponse(template.render(context, request))
