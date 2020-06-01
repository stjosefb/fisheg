from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from fisheg import settings
from PIL import Image
from skimage import measure
from shapely.geometry import Polygon
import json
import os
import numpy as np


def index(request, list_seg_in=None, method='GET'):
    # return HttpResponse("Hello, world. You're at the annotation index.")
    #message = ''
    #if 'message' in request.GET:
    #    message = request.GET['message']
    if method == 'POST':
        input = request.POST
    else:
        input = request.GET
    is_ref_dataset = False
    if 'refdataset' in input:
        is_ref_dataset = True
        ref_dataset = input['refdataset']
    dataset = input['dataset']
    data_id = input['data_id']

    # get image
    image_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS,
                                    data_id + '.json'])


    with open(image_info_file) as f:
        image_info = json.load(f)
        image = image_info['image']
        protocol = 'https' if request.is_secure() else 'http'
        image_url = protocol + '://' + get_current_site(request).domain + '/' + image

    # get polygon segmentation annotations
    if list_seg_in is None:
        list_seg = []
        if is_ref_dataset:
            polygon_annot_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_REFDATASETS,
                                        ref_dataset, settings.DIR_DATASETS_ANNOTATIONS, data_id + '.json'])
        else:
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
    else:
        list_seg = list_seg_in

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


def upload_segmask_file(request):
    f = request.FILES['segmask_file']
    pim = Image.open(f)
    #width, height = im.size
    #print(width, height)

    mask = np.array(pim)
    #print(npim.shape)
    #print(npim)

    segmentations = create_segmentations(mask)

    list_seg = []
    for segmentation in segmentations:
        list_x = [str(x) for x in segmentation[::2]]
        list_y = [str(y) for y in segmentation[1::2]]
        str_list_x = ','.join(list_x)
        str_list_y = ','.join(list_y)
        seg = {'x': str_list_x, 'y': str_list_y}
        list_seg.append(seg)

    return index(request, list_seg, 'POST')


def create_segmentations(mask):
    contours = measure.find_contours(mask, 0.5, positive_orientation='low')

    segmentations = []
    polygons = []
    for contour in contours:
        # Flip from (row, col) representation to (x, y)
        # and subtract the padding pixel
        for i in range(len(contour)):
            row, col = contour[i]
            contour[i] = (col - 1, row - 1)

        # Make a polygon and simplify it
        poly = Polygon(contour)
        poly = poly.simplify(1.0, preserve_topology=False)
        polygons.append(poly)
        segmentation = np.array(poly.exterior.coords).ravel().tolist()
        segmentations.append(segmentation)

    return segmentations