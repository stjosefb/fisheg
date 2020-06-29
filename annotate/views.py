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

    #annot_method = input_req['method'] if 'method' in input_req else 'default'
    if 'method' in input_req:
        annot_method = input_req['method']
    else:
        annot_method = ''

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
                annot = json.load(f)
                if annot_method == '':
                    if 'method' in annot:
                        annot_method = annot['method']
                    else:
                        annot_method = 'default'
                if annot_method == 'default':
                    polygon_annot = annot[annot_method]
                elif annot_method == 'freelabel':
                    if annot_method in annot:
                        polygon_annot = annot[annot_method]['shapes']
                    else:
                        polygon_annot = []
                for key, region in enumerate(polygon_annot):
                    list_x = [str(x) for x in region[::2]]
                    list_y = [str(y) for y in region[1::2]]
                    str_list_x = ','.join(list_x)
                    str_list_y = ','.join(list_y)
                    if annot_method == 'freelabel':
                        seg = {'x': str_list_x, 'y': str_list_y, 'category': annot[annot_method]['classes'][key]}
                    else:
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
        'method': annot_method
        # 'message': message
    }
    if is_ref_dataset:
        context['ref_dataset'] = ref_dataset
    return HttpResponse(template.render(context, request))


def save(request):
    data_id = request.POST['data_id']
    dataset = request.POST['dataset']
    annot = request.POST['annot']
    categories = request.POST['categories']
    annot_method = request.POST['method']
    score = request.POST['scores']
    polygon_segmentations = request.POST['polygon_segmentations']
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
        list_cats = json.loads(categories)
        if len(list_seg) > 0:
            data = {}

            if annot_method == 'default':
                data[annot_method] = list_seg
            elif annot_method == 'freelabel':
                data['default'] = json.loads(polygon_segmentations)
                data[annot_method] = {
                    'shapes': list_seg,
                    'classes': list_cats
                }
            data['method'] = annot_method
            if is_ref_dataset:
                scores = score.split(';')
                if len(scores) == 2:
                    data['score_jaccard'] = scores[0]
                    data['score_dice'] = scores[1]
                else:
                    data['score_jaccard'] = None
                    data['score_dice'] = None
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


# mask file
def upload_segmask_file(request):
    f = request.FILES['segmask_file']
    segmentations = get_segmentations_from_file(f)

    list_seg = []
    for segmentation in segmentations:
        if len(segmentation) > 0:
            list_x = [str(x) for x in segmentation[::2]]
            list_y = [str(y) for y in segmentation[1::2]]
            str_list_x = ','.join(list_x)
            str_list_y = ','.join(list_y)
            seg = {'x': str_list_x, 'y': str_list_y}
            list_seg.append(seg)
            break

    return index(request, list_seg, 'POST')


# mask file
def get_segmentations_from_file(image_file, type='name'):
    if type == 'name':
        pim = Image.open(image_file)
    else:  # type == 'content'
        pim = Image.open(BytesIO(image_file)).convert('1')
    #width, height = im.size
    #print(width, height)

    mask = np.array(pim)
    #print(mask.shape)
    #print(npim)

    segmentations = create_segmentations(mask)
    #print(segmentations)
    segmentations = [x for idx,x in enumerate(segmentations) if len(x) > 0 and idx == 0]

    return segmentations


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
            annot_obj = json.load(f)
            annot_src = annot_obj['default']
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

        score, score2 = compare_annot(img_file, annot_check, annot_src)
        #score = 0.5

        response = {
            "success": True,
            "message": "Scoring done",
            "score": score,
            "score2": score2,
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
    score, _, score3 = iou_mask(mask1, mask2)
    #score = 0.3
    return score, score3


def compare_annot2(img_file, annot, img_mask_file):
    img = Image.open(img_file)
    #print(img.size)
    mask1, img_mask_1 = get_img_mask(img, annot)
    #print(mask1)
    #mask2 = get_img_mask(img, annot_src)
    #img2 = Image.open(img_mask_file)
    #print(img_mask_file)
    #img_mask = Image.open(img_mask_file).convert("RGBA")
    img_mask = Image.open(BytesIO(img_mask_file)).convert('L')
    #print(img_mask)
    #img_mask = Image.open(BytesIO(img_mask_file)).convert("RGBA")
    #img_mask = Image.open(img_mask_file)
    mask2 = np.array(img_mask)
    #print(np.count_nonzero(mask2 == True))
    #print(np.count_nonzero(mask2 == False))
    #print(mask1.size)
    #print(mask2.size)
    mask2 = np.invert(mask2)
    #print(mask1.size)
    #print(mask2.size)
    mask2 = mask2.astype(int)
    #print(np.count_nonzero(mask2))
    #mask2 = mask2.ravel()
    mask2 = mask2.reshape(img_mask.width * img_mask.height)
    #print(mask1.size)
    #print(mask2.size)
    #print(mask1)
    #print(mask2)
    #print(np.count_nonzero(mask1))
    #print(np.count_nonzero(mask2))
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
    #print(np.count_nonzero(mask_and))
    mask_or = np.logical_or(mask1, mask2)
    #print(np.count_nonzero(mask_or))
    n_intersect = np.count_nonzero(mask_and)
    n_union = np.count_nonzero(mask_or)
    iou = n_intersect / n_union
    iou2 = np.count_nonzero(mask1) / n_union
    iou3 = (2 * n_intersect) / (np.count_nonzero(mask1) + np.count_nonzero(mask2))
    return iou, iou2, iou3


# Freelabel
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
            annot_obj = json.load(f)
            annot_src = annot_obj['default']
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

    segmentation = get_segmentations_from_file(r.content, type="content")
    #print(segmentation)

    # response
    response = {
        "success": True,
        "message": "Done",
        "score": score,
        "score_2": score2,
        "score_3": score3,
        "image_base64": uri,
        "image_base64_2": uri2,
        "polygon_segmentations": segmentation
    }
    return JsonResponse(response)
