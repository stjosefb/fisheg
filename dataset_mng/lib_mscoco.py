from collections import OrderedDict
from datetime import datetime
from fisheg import settings
from io import BytesIO
from PIL import Image
import base64
import json
import numpy as np
import os


def prepare(dataset, request):
    data = {}

    data['info'] = prepare_info(dataset, request)
    data['licenses'] = prepare_licenses(dataset)
    data['categories'], dict_category_ids = prepare_categories(dataset)
    data['images'], dict_file_id_image_id = prepare_images(dataset, request)
    data['annotations'] = prepare_annotations(dataset, dict_category_ids, dict_file_id_image_id)

    return data


def prepare_annotations(dataset, dict_category_ids, dict_file_id_image_id):
    annots = []

    # annotations folder
    annot_folder = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_ANNOTATIONS])

    # list json files inside annotations folder
    annot_files = [f for f in os.listdir(annot_folder) if
                  os.path.isfile(os.path.join(annot_folder, f))]

    for idx,annot_file in enumerate(annot_files):
        with open(annot_folder+'/'+annot_file) as json_file:
            try:
                list_file_name_ext = annot_file.split('.')
                file_id = list_file_name_ext[0]
                image_id = dict_file_id_image_id[file_id]

                annot_content = json.load(json_file)
                annot_info = get_annot_info(annot_content)

                annot = {
                    'image_id': image_id,
                    'id': idx+1,
                    'iscrowd': 1,
                    'category_id': dict_category_ids[annot_info['category_id']],
                    'area': annot_info['area'],
                    'bbox': annot_info['bbox'],
                    'segmentation': {
                        'size': [annot_info['height'], annot_info['width']],
                        'counts': annot_info['counts'],
                        #'sum': sum(annot_info['counts'])
                    }
                }

                annots.append(annot)
            except:
                pass

    return annots


def get_annot_info(annot_content):
    annot_info = {}

    # category
    set_classes = set(annot_content['freelabel']['classes'])
    set_classes.remove('background')
    list_classes = list(set_classes)
    annot_info['category_id'] = list_classes[0]
    #annot_info['category_id'] = 1

    # mask
    encoded_elmts_img_base64 = annot_content['imagemask'].split(',', 1)
    img_content = base64.decodebytes(encoded_elmts_img_base64[1].encode('ascii'))
    img_mask = Image.open(BytesIO(img_content)).convert('L')

    # size
    width, height = img_mask.size
    annot_info['width'] = width
    annot_info['height'] = height

    # area
    arr = np.array(img_mask)
    arr = arr < 225
    area = np.count_nonzero(arr)
    annot_info['area'] = area

    # bounding box
    out_tuple = np.nonzero(arr)
    y1 = out_tuple[0][0]
    y2 = out_tuple[0][-1]
    x1 = np.amin(out_tuple[1])
    x2 = np.amax(out_tuple[1])
    h = y2-y1
    w = x2-x1
    #annot_info['bbox'] = y2.item()
    annot_info['bbox'] = [x1.item(),y1.item(),w.item(),h.item()]
    #annot_info['bbox'] = [x1.item(), y1.item(), x2.item(), y2.item()]

    counts = []
    count = 0
    count_mode = 0 # background
    for x in range(width):
        for y in range(height):
            if count_mode == 0:
                if arr[y][x] == True:
                    counts.append(count)
                    count_mode = 1
                    count = 1
                else:
                    count = count + 1
            else:
                if arr[y][x] == False:
                    counts.append(count)
                    count_mode = 0
                    count = 1
                else:
                    count = count + 1
    counts.append(count)

    annot_info['counts'] = counts

    return annot_info


def prepare_images(dataset, request):
    dict_image_ids = OrderedDict()
    dict_file_id_image_id = {}
    images = []

    # images (infos) folder
    info_folder = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS])

    # list json files inside images (infos) folder
    info_files = [f for f in os.listdir(info_folder) if
                  os.path.isfile(os.path.join(info_folder, f))]

    # list images path
    image_path_set = set()
    dict_file_id_image_path = {}
    for info_file in info_files:
        with open(info_folder+'/'+info_file) as json_file:
            try:
                list_file_name_ext = info_file.split('.')
                file_id = list_file_name_ext[0]

                info_content = json.load(json_file)
                image_path_set.add(info_content['image'])
                dict_file_id_image_path[file_id] = info_content['image']
            except:
                pass
    image_path_list = list(image_path_set)

    # dictionary image ids (mapping path to id)
    for idx, image_path in enumerate(image_path_list):
        image_id = idx+1
        dict_image_ids[image_path] = image_id

    # dict_file_id_image_path
    for key, value in dict_file_id_image_path.items():
        dict_file_id_image_id[key] = dict_image_ids[value]

    # images
    for key, value in dict_image_ids.items():
        base_url = get_base_url(request)
        list_file_dir_name = key.split('/')

        im = Image.open(settings.BASE_DIR+'/'+key)
        width, height = im.size

        image = {
            'id': value,
            'license': 1,
            'file_name': list_file_dir_name[-1],
            'coco_url': base_url+'/'+key,
            'width': width,
            'height': height
        }
        images.append(image)
        #"date_captured": "2013-11-14 11:18:45",

    return images, dict_file_id_image_id


def get_base_url(request):
    if request.is_secure():
        protocol = 'https://'
    else:
        protocol = 'http://'
    base_url = protocol + request.get_host()
    return base_url


def prepare_categories(dataset):
    dict_category_ids = {}
    categories = []

    # info file
    dataset_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.FILENAME_DATASET_INFO])

    # data
    info_content = None
    if os.path.exists(dataset_info_file):
        with open(dataset_info_file, 'r') as json_file:
            try:
                info_content = json.load(json_file)

            except Exception as e:
                #error = str(e)
                pass

    if info_content is not None:
        for class_ in info_content['classes']:
            category = {}
            category['supercategory'] = 'thing'
            category['id'] = class_['id'] - 1
            category['name'] = class_['name']
            categories.append(category)

            dict_category_ids[category['name']] = category['id']

    return categories, dict_category_ids


def prepare_info(dataset, request):
    now = datetime.now()
    base_url = get_base_url(request)
    dataset_name = get_title(dataset)

    info = {}
    info['description'] = dataset_name+' dataset'
    info['url'] = base_url+'/dataset/'+dataset
    info['version'] = '1.0'
    info['year'] = now.year
    info['contributor'] = dataset_name+' dataset contributors'
    info['date_created'] = now.strftime("%Y/%m/%d")

    return info


def prepare_licenses(dataset):
    licenses = [{
        'url': 'http://flickr.com/commons/usage/',
        'id': 1,
        'name': 'No known copyright restrictions'
    }]

    return licenses


def get_title(dataset):
    dataset_name = dataset.replace('_',' ').title()
    return dataset_name
