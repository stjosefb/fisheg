from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import os
import time
from fisheg import settings


def index(request):
    message = ''
    if 'message' in request.GET:
        message = request.GET['message']
    template = loader.get_template('dataset_mng/index.html')
    subfolders = [f.name for f in os.scandir(settings.BASE_DATASETS_PATH) if f.is_dir()]
    context = {
        'dataset_list': subfolders,
        'message': message
    }
    return HttpResponse(template.render(context, request))


def create_dataset(request):
    try:
        dataset = request.POST['new_dataset']
        #print(folder)
        os.mkdir(settings.BASE_DATASETS_PATH+'/'+dataset)
    except OSError:
        #pass
        message = 'Failed'
        #print("Creation of the directory %s failed" % path)
    else:
        #pass
        message = 'Successful'
        #print("Successfully created the directory %s " % path)
    return HttpResponseRedirect('.'+'?message='+message)
    #return HttpResponse(folder)


def manage_annot(request):
    message = ''
    if 'message' in request.GET:
        message = request.GET['message']
    template = loader.get_template('dataset_mng/annot_mng.html')
    dataset = request.GET['dataset']
    #files = [f.name for f in os.scandir(BASE_IMAGES_PATH+'/'+folder)]
    annot_list = []
    img_folder_list = [f.name for f in os.scandir(settings.BASE_IMAGES_PATH)]
    #a = settings.MEDIA_ROOT
    context = {
        'annot_list': annot_list,
        'img_folder_list': img_folder_list,
        'dataset': dataset,
        'message': message,
    }
    return HttpResponse(template.render(context, request))
