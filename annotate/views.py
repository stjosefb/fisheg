from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from fisheg import settings
import json
import os


def index(request):
    # return HttpResponse("Hello, world. You're at the annotation index.")
    #message = ''
    #if 'message' in request.GET:
    #    message = request.GET['message']
    is_ref_dataset = False
    if 'refdataset' in request.GET:
        is_ref_dataset = True
        ref_dataset = request.GET['refdataset']
    dataset = request.GET['dataset']
    data_id = request.GET['data_id']

    # get image
    image_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS,
                                data_id + '.json'])
    with open(image_info_file) as f:
        image_info = json.load(f)
        image = image_info['image']
        protocol = 'https' if request.is_secure() else 'http'
        image_url = protocol + '://' + get_current_site(request).domain + '/' + image

    # get polygon segmentation annotations
    list_seg = []
    polygon_annot_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_ANNOTATIONS,
                                data_id + '.json'])
    try:
        with open(polygon_annot_file) as f:
            polygon_annot = json.load(f)
            for region in polygon_annot:
                list_x = [str(x) for x in region[::2]]
                list_y = [str(y) for y in region[1::2]]
                str_list_x = ','.join(list_x)
                str_list_y = ','.join(list_y)
                seg = {'x': str_list_x, 'y': str_list_y}
                list_seg.append(seg)
    except FileNotFoundError:
        pass

    # display
    template = loader.get_template('annotate/index.html')
    # subfolders = [f.name for f in os.scandir(settings.BASE_DATASETS_PATH) if f.is_dir()]
    context = {
        'dataset': dataset,
        'data_id': data_id,
        'is_ref_dataset': is_ref_dataset,
        #'image': image,
        'image_url': image_url,
        #'list_x': str_list_x,
        #'list_y': str_list_y,
        'list_seg': list_seg
        # 'message': message
    }
    if is_ref_dataset:
        context['ref_dataset'] = ref_dataset
    return HttpResponse(template.render(context, request))


def save(request):
    data_id = request.POST['data_id']
    dataset = request.POST['dataset']
    annot = request.POST['annot']
    is_ref_dataset = False
    if 'refdataset' in request.POST:
        is_ref_dataset = True
        ref_dataset = request.POST['refdataset']

    if is_ref_dataset:
        datasets_dir = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_REFDATASETS,
                                 ref_dataset, settings.DIR_DATASETS_ANNOTATIONS])
    else:
        datasets_dir = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_ANNOTATIONS])

    #print(annot)
    #data = []
    if (annot != ''):
        list_seg = json.loads(annot)
        if len(list_seg) > 0:
            data = list_seg
            with open(datasets_dir + '/' + str(data_id) + '.json', 'w') as f:
                json.dump(data, f)
        else:
            os.remove(datasets_dir + '/' + str(data_id) + '.json')

    response = {
        "success": True,
        "message": "Annotation was saved",
    }
    return JsonResponse(response)