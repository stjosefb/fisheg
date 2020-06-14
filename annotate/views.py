from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from fisheg import settings
from PIL import Image, ImageDraw
from skimage import measure
from shapely.geometry import Polygon
import json
import os
import numpy as np
import requests
import base64
from io import BytesIO


def index(request, list_seg_in=None, method='GET'):
    # return HttpResponse("Hello, world. You're at the annotation index.")
    #message = ''
    #if 'message' in request.GET:
    #    message = request.GET['message']
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
    method = input_req['method'] if 'method' in input_req else 'default'

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
        'image_width': image_width,
        'image_height': image_height,
        #'list_x': str_list_x,
        #'list_y': str_list_y,
        'list_seg': list_seg,
        'method': method
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
            path = datasets_dir + '/' + str(data_id) + '.json'
            if os.path.exists(path):
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


def check_score(request):
    data_id = request.POST['data_id']
    dataset = request.POST['dataset']
    annot = request.POST['annot']
    annot_check = json.loads(annot)

    annot_src = ''
    polygon_annot_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_ANNOTATIONS,
                                   data_id + '.json'])
    try:
        with open(polygon_annot_file) as f:
            annot_src = json.load(f)
    except FileNotFoundError:
        pass

    if annot_src != '':
        image_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS,
                                    data_id + '.json'])

        with open(image_info_file) as f:
            image_info = json.load(f)
            img_file = image_info['image']

        #img = Image.open(img_file)
        #print(img.size)

        score = compare_annot(img_file, annot_check, annot_src)
        #score = 0.5

        response = {
            "success": True,
            "message": "Scoring done",
            "score": score,
            "annot": annot_check,
            "annot_src": annot_src
        }
    else:
        response = {
            "success": False,
            "message": "Scoring cannot be done",
            "score": -1,
            "annot": annot_check,
            "annot_src": annot_src
        }
    return JsonResponse(response)


def compare_annot(img_file, annot, annot_src):
    img = Image.open(img_file)
    #print(img.size)
    mask1, _ = get_img_mask(img, annot)
    #print(mask1)
    mask2, _ = get_img_mask(img, annot_src)
    score, _, _ = iou_mask(mask1, mask2)
    #score = 0.3
    return score


def compare_annot2(img_file, annot, img_mask_file):
    img = Image.open(img_file)
    #print(img.size)
    mask1, img_mask_1 = get_img_mask(img, annot)
    #print(mask1)
    #mask2 = get_img_mask(img, annot_src)
    #img2 = Image.open(img_mask_file)
    #print(img_mask_file)
    #img_mask = Image.open(img_mask_file).convert("RGBA")
    img_mask = Image.open(BytesIO(img_mask_file)).convert('1')
    #img_mask = Image.open(img_mask_file)
    mask2 = np.array(img_mask)
    mask2 = mask2.ravel()
    mask2 = np.invert(mask2)
    print(mask1)
    print(mask2)
    score, score2, score3 = iou_mask(mask1, mask2)

    #img_mask_1 = Image.fromarray(mask2d)
    buffered = BytesIO()
    img_mask_1.save(buffered, format="PNG")
    im_bytes = buffered.getvalue()
    #img_mask_file_1 = base64.b64encode(buffered.getvalue())

    #score = 0.3
    return score, im_bytes, score2, score3


def get_img_mask(img, annot):
    size = img.size
    img2 = Image.new('L', size, 'black')
    draw = ImageDraw.Draw(img2)
    for polygon in annot:
        draw.polygon(polygon, fill='white')

    mask2d = np.array(img2)
    mask = mask2d.reshape(img2.width * img2.height)

    return mask, img2


def iou_mask(mask1, mask2):
    mask_and = np.logical_and(mask1, mask2)
    mask_or = np.logical_or(mask1, mask2)
    n_intersect = np.count_nonzero(mask_and)
    n_union = np.count_nonzero(mask_or)
    iou = n_intersect / n_union
    iou2 = np.count_nonzero(mask1) / n_union
    iou3 = (2 * n_intersect) / (np.count_nonzero(mask1) + np.count_nonzero(mask2))
    return iou, iou2, iou3


def grow_refine_traces(request):
    # input params
    dataset = request.POST['dataset']
    data_id = request.POST['data_id']

    # payload
    payload = {
        'img': request.POST['img'],
        'ID': request.POST['ID'],
        'weight': request.POST['weight'],
        'm': request.POST['m']
    }
    img_sizes = request.POST.getlist('img_size[]')
    #for img_size in img_sizes:
    payload['img_size[]'] = img_sizes
    traces = request.POST.getlist('trace[]')
    #for trace in traces:
    payload['trace[]'] = traces

    # request
    url = 'http://localhost:9000/freelabel/refine2/'
    r = requests.post(url, data=payload)

    # result
    uri = ("data:" +
           r.headers['Content-Type'] + ";" +
           "base64," + base64.b64encode(r.content).decode('ascii'))

    # reference annotation
    annot_src = ''
    polygon_annot_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_ANNOTATIONS,
                                   data_id + '.json'])
    #print(polygon_annot_file)
    try:
        with open(polygon_annot_file) as f:
            annot_src = json.load(f)
    except FileNotFoundError:
        pass
    #print(annot_src)
    if annot_src != '':
        image_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS,
                                    data_id + '.json'])
        #print(image_info_file)
        with open(image_info_file) as f:
            image_info = json.load(f)
            img_file = image_info['image']


    # score
    #print(r.content)
    score, img_mask_1, score2, score3 = compare_annot2(img_file, annot_src, r.content)

    uri2 = ("data:" +
           "image/png" + ";" +
           "base64," + base64.b64encode(img_mask_1).decode('ascii'))

    # response
    response = {
        "success": True,
        "message": "Done",
        "score": score,
        "score_2": score2,
        "score_3": score3,
        "image_base64": uri,
        "image_base64_2": uri2
    }
    return JsonResponse(response)
