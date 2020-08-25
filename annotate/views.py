from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from fisheg import settings
from PIL import Image

import json
import os
import requests
import base64
import time

import annotate.lib_mask as lib_mask


def index(request, list_seg_in=None, method='GET', data={}):
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

    if 'method' in input_req:
        annot_method = input_req['method']
    else:
        annot_method = ''

    # init
    score_jaccard = None
    score_dice = None
    annot = None

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
                elif annot_method == 'imagemask':
                    polygon_annot = annot['default']
                    data = {}
                    #data['base64image_transparent'] = lib_mask.img_base64_change_mask_color_transparent(annot[annot_method]) if annot_method in annot else '#'
                    data['base64image'] = annot[annot_method] if annot_method in annot else '#'
                    data['showRegion'] = False
                for key, region in enumerate(polygon_annot):
                    list_x = [str(x) for x in region[::2]]
                    list_y = [str(y) for y in region[1::2]]
                    str_list_x = ','.join(list_x)
                    str_list_y = ','.join(list_y)
                    if annot_method == 'freelabel':
                        if 'trace_types' in annot[annot_method]:
                            shape = annot[annot_method]['trace_types'][key]
                        else:
                            shape = 'polyline'
                        seg = {
                               'category': annot[annot_method]['classes'][key],
                               'shape': shape
                               }
                        if shape == 'polyline' or shape == 'polygon':
                            seg['x'] = str_list_x
                            seg['y'] = str_list_y
                        elif shape == 'rect':
                            seg['x'] = region[0]
                            seg['y'] = region[1]
                            seg['width'] = region[2] - region[0]
                            seg['height'] = region[-1] - region[1]
                    else:
                        seg = {'x': str_list_x, 'y': str_list_y}
                    list_seg.append(seg)
                score_jaccard = annot['score_jaccard']
                score_dice = annot['score_dice']
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
        'method': annot_method if annot_method != '' else 'freelabel'
        # 'message': message
    }
    if annot:
        if annot_method == annot['method']:
            if score_jaccard is not None and score_dice is not None:
                context['score'] = score_jaccard + ' ' + score_dice
    if data:
        context.update(data)
    if 'showRegion' not in context:
        context['showRegion'] = True
    if is_ref_dataset:
        context['ref_dataset'] = ref_dataset
    return HttpResponse(template.render(context, request))


def save(request):
    data_id = request.POST['data_id']
    dataset = request.POST['dataset']
    annot = request.POST['annot']
    categories = request.POST['categories']
    shapes = request.POST['shapes']
    annot_method = request.POST['method']
    score = request.POST['scores']
    polygon_segmentations = request.POST['polygon_segmentations']
    base64_img_mask = request.POST['base64_img_mask']
    ts_diff = request.POST['ts_diff']
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
        list_trace_types = json.loads(shapes)
        if len(list_seg) > 0:
            data = {}

            if annot_method == 'default':
                data[annot_method] = list_seg
            elif annot_method == 'freelabel':
                data['default'] = json.loads(polygon_segmentations)
                data['imagemask'] = base64_img_mask
                data[annot_method] = {
                    'shapes': list_seg,
                    'trace_types': list_trace_types,
                    'classes': list_cats,
                    'ts_diff': ts_diff
                }
            elif annot_method == 'imagemask':
                data['default'] = list_seg
                data[annot_method] = base64_img_mask
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
    if request.method == 'GET':
        return HttpResponse('')
    f = request.FILES['segmask_file']
    segmentations, base64image = lib_mask.get_polygons_from_img_mask(f)

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

    data = {'base64image': lib_mask.img_base64_change_mask_color_transparent(base64image), 'showRegion': True}
    #return JsonResponse(data)
    return index(request, list_seg, 'POST', data)


def check_score(request):
    data_id = request.POST['data_id']
    dataset = request.POST['dataset']
    annot = request.POST['annot']
    method = request.POST['method']

    annot_src = ''
    polygon_annot_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_ANNOTATIONS,
                                   data_id + '.json'])
    try:
        with open(polygon_annot_file) as f:
            annot_obj = json.load(f)
            #annot_src = annot_obj['default']
            annot_src = annot_obj[annot_obj['method']]
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

        if annot_obj['method'] == 'imagemask':
            encoded_img_elmts_1 = annot_src.split(',', 1)
            img_content_mask_1 = base64.decodebytes(encoded_img_elmts_1[1].encode('ascii'))
            if method == 'imagemask':
                encoded_img_elmts_2 = annot.split(',', 1)
                img_content_mask_2 = base64.decodebytes(encoded_img_elmts_2[1].encode('ascii'))
                img_content_mask_2 = lib_mask.img_content_change_mask_color_solid(img_content_mask_2)
                #annot_check = annot
                score, score2, _, _ = lib_mask.annot_img_content_mask_compare(img_content_mask_1, img_content_mask_2
                                                                              , invert=True)
            else:
                annot_check = json.loads(annot)
                score, score2, _, _ = lib_mask.annot_polygon_compare_img_content_mask(
                    img_file, annot_check, img_content_mask_1, invert=True
                )

            #uri2 = ("data:" +
            #    "image/png" + ";" +
            #    "base64," + encoded_img_elmts[1])
        else:
            if method == 'imagemask':
                encoded_img_elmts_2 = annot.split(',', 1)
                img_content_mask_2 = base64.decodebytes(encoded_img_elmts_2[1].encode('ascii'))
                img_content_mask_2 = lib_mask.img_content_change_mask_color_solid(img_content_mask_2)
                score, score2, _, _ = lib_mask.annot_polygon_compare_img_content_mask(
                    img_file, annot_src, img_content_mask_2, invert=False
                )
                print(score)
            else:
                annot_check = json.loads(annot)
                score, score2 = lib_mask.annot_polygon_compare(img_file, annot_check, annot_src)
        #score = 0.5

        response = {
            "success": True,
            "message": "Scoring done",
            "score": score,
            "score2": score2,
            #"image_base64": uri2,
            #"annot": annot_check,
            #"annot_src": annot_src
        }
    else:
        response = {
            "success": False,
            "message": "Scoring cannot be done",
            "score": -1,
            #"annot": [],
            #"annot_src": []
        }
    return JsonResponse(response)


# freelabel
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
    #url = 'http://142.93.169.91:9000/freelabel/refine2/'
    ts_1 = time.time()
    r = requests.post(url, data=payload)
    ts_2 = time.time()
    ts_diff = ts_2 - ts_1

    # # reference annotation
    # annot_src = ''
    # polygon_annot_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_ANNOTATIONS,
    #                                data_id + '.json'])
    # #print(polygon_annot_file)
    # try:
    #     with open(polygon_annot_file) as f:
    #         annot_obj = json.load(f)
    #         annot_src = annot_obj['default']
    # except FileNotFoundError:
    #     pass
    # #print(annot_src)
    # if annot_src != '':
    #     image_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS,
    #                                 data_id + '.json'])
    #     #print(image_info_file)
    #     with open(image_info_file) as f:
    #         image_info = json.load(f)
    #         img_file = image_info['image']
    #
    #
    # # score
    # #print(r.content)
    # score_jaccard, score_dice, img_mask_1 = lib_mask.annot_polygon_compare_img_content_mask(img_file, annot_src, r.content)

    # scoring
    image_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS,
                                data_id + '.json'])
    polygon_annot_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_ANNOTATIONS,
                                   data_id + '.json'])
    score_jaccard, score_dice, img_mask_1, img_mask_2 = lib_mask.score_against_ref_by_img_content(image_info_file, polygon_annot_file, r.content)

    # image mask: freelabel
    uri_img_mask_freelabel = ("data:" +
           r.headers['Content-Type'] + ";" +
           "base64," + base64.b64encode(img_mask_2).decode('ascii'))

    # image mask: reference
    uri_img_mask_ref = ("data:" +
           "image/png" + ";" +
           "base64," + base64.b64encode(img_mask_1).decode('ascii'))

    # image mask to polygons
    segmentation = lib_mask.get_polygons_from_img_mask(r.content, type="content")
    #print(segmentation)

    # response
    response = {
        "success": True,
        "message": "Done",
        "score": score_jaccard,
        "score_2": None,
        "score_3": score_dice,
        "image_base64_freelabel": uri_img_mask_freelabel,
        "image_base64_ref": uri_img_mask_ref,
        "polygon_segmentations": segmentation,
        "ts_diff": ts_diff
    }
    return JsonResponse(response)
