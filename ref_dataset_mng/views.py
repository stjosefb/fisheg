from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
import json
import os
from fisheg import settings
import time
import shutil


def index(request):
    # parameters
    parent_dataset = request.GET['dataset']
    message = ''
    if 'message' in request.GET:
        message = request.GET['message']


    refdatasets_dir = '/'.join([settings.BASE_DATASETS_PATH, parent_dataset, settings.DIR_DATASETS_REFDATASETS])
    subfolders = [f.name for f in os.scandir(refdatasets_dir) if f.is_dir()]

    # display
    context = {
        'dataset': parent_dataset,
        'ref_dataset_list': subfolders,
        'message': message
    }
    template = loader.get_template('ref_dataset_mng/index.html')
    return HttpResponse(template.render(context, request))


def create_ref_dataset(request):
    try:
        parent_dataset = request.POST['dataset']
        referencing_dataset = request.POST['refdataset']

        #print(folder)

        refdatasets_dir = '/'.join([settings.BASE_DATASETS_PATH, parent_dataset,
                                    settings.DIR_DATASETS_REFDATASETS, referencing_dataset])

        os.mkdir(refdatasets_dir)
        os.mkdir('/'.join([refdatasets_dir, settings.DIR_DATASETS_ANNOTATIONS]))
    except OSError:
        #pass
        message = 'Failed'
        #print("Creation of the directory %s failed" % path)
    else:
        #pass
        message = 'Successful'
        #print("Successfully created the directory %s " % path)
    return HttpResponseRedirect('.'+'?message='+message+'&dataset='+parent_dataset)
    #return HttpResponse(folder)


def manage_annot(request):
    # parameters
    message = ''
    if 'message' in request.GET:
        message = request.GET['message']
    dataset = request.GET['dataset']
    ref_dataset = request.GET['refdataset']

    # directories
    datasets_info_dir = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS])
    ref_datasets_annot_dir = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_REFDATASETS,
                                       ref_dataset, settings.DIR_DATASETS_ANNOTATIONS])

    # list of image data from parent dataset
    info_files = [f for f in os.listdir(datasets_info_dir) if
                  os.path.isfile(os.path.join(datasets_info_dir, f))]

    # annotations info of image data
    annotations = []
    for info_file in info_files:
        with open(datasets_info_dir+'/'+info_file) as json_file:
            try:
                info_content = json.load(json_file)
                info_content['id'] = int(os.path.splitext(info_file)[0])
                #info_content['is_annotated'] = False
                info_content['is_annotated'] = os.path.exists(ref_datasets_annot_dir+'/'+info_file)
                annotations.append(info_content)
            except:
                pass
    annotations = sorted(annotations, key=lambda i: (int(i['id'])))

    # display
    context = {
        'annotations': annotations,
        'dataset': dataset,
        'ref_dataset': ref_dataset,
        'message': message,
    }
    template = loader.get_template('ref_dataset_mng/annot_mng.html')
    return HttpResponse(template.render(context, request))


def remove_ref_dataset(request):
    try:
        parent_dataset = request.POST['parent_dataset']
        ref_dataset = request.POST['ref_dataset']
        src = '/'.join([settings.BASE_DATASETS_PATH, parent_dataset, settings.DIR_DATASETS_REFDATASETS, ref_dataset])
        dst = '/'.join([settings.BASE_DATASETS_PATH, parent_dataset, settings.DIR_DATASETS_DELETED_REFDATASETS, str(int(time.time()))])
        shutil.move(src, dst)
    except OSError:
        #pass
        message = 'Failed '+ src + ' ' + dst
        #print("Creation of the directory %s failed" % path)
    else:
        #pass
        message = 'Successful'
        #print("Successfully created the directory %s " % path)
    return HttpResponseRedirect('.'+'?message='+message+'&dataset='+parent_dataset)
