from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, JsonResponse
from django.template import loader
from fisheg import settings
import json


def index(request):
    # return HttpResponse("Hello, world. You're at the annotation index.")
    #message = ''
    #if 'message' in request.GET:
    #    message = request.GET['message']
    dataset = request.GET['dataset']
    data_id = request.GET['data_id']
    template = loader.get_template('annotate/index.html')
    # subfolders = [f.name for f in os.scandir(settings.BASE_DATASETS_PATH) if f.is_dir()]
    context = {
        'dataset': dataset,
        'data_id': data_id
        # 'message': message
    }
    return HttpResponse(template.render(context, request))


def save(request):
    data_id = request.POST['data_id']
    dataset = request.POST['dataset']

    datasets_dir = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_ANNOTATIONS])

    data = [[]]
    with open(datasets_dir + '/' + str(data_id) + '.json', 'w') as f:
        json.dump(data, f)

    response = {
        "success": True,
        "message": "Annotation was saved",
    }
    return JsonResponse(response)