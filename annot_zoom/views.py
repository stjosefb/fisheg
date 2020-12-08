from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from fisheg import settings
from PIL import Image

import json


def index(request, method='GET'):
    # params
    if method == 'POST':
        input_req = request.POST
    else:
        input_req = request.GET
    is_ref_dataset = False
    if 'refdataset' in input_req:
        is_ref_dataset = True
        ref_dataset = input_req['refdataset']
    dataset = input_req['dataset']
    data_id = input_req['data_id']

    # get image
    image_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS,
                                    data_id + '.json'])
    with open(image_info_file) as f:
        image_info = json.load(f)
        image = image_info['image']
        protocol = 'https' if request.is_secure() else 'http'
        image_url = protocol + '://' + get_current_site(request).domain + '/' + image
        img = Image.open(image)
        image_width = img.size[0]
        image_height = img.size[1]

    # get image mask
    image_mask_url = None
    polygon_annot_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_REFDATASETS,
                                   ref_dataset, settings.DIR_DATASETS_ANNOTATIONS, data_id + '.json'])
    try:
        with open(polygon_annot_file) as f:
            annot = json.load(f)
            if 'imagemask' in annot:
                image_mask_url = annot['imagemask']
    except FileNotFoundError:
        pass

    # display
    template = loader.get_template('annot_zoom/index.html')
    # subfolders = [f.name for f in os.scandir(settings.BASE_DATASETS_PATH) if f.is_dir()]
    context = {
        'dataset': dataset,
        'image_url': image_url,
        'image_mask_url': image_mask_url,
        'image_width': image_width,
        'image_height': image_height,
        'image_prop': image_width/image_height,
    }
    return HttpResponse(template.render(context, request))
