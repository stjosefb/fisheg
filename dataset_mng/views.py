from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
import json
import os
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
        os.mkdir('/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS]))
        os.mkdir('/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_ANNOTATIONS]))
        os.mkdir('/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_REFDATASETS]))
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
    img_folder_list = [f.name for f in os.scandir(settings.BASE_IMAGES_PATH) if
                       os.path.isdir(os.path.join(settings.BASE_IMAGES_PATH, f.name))]
    #a = settings.MEDIA_ROOT
    context = {
        'annot_list': annot_list,
        'img_folder_list': img_folder_list,
        'dataset': dataset,
        'message': message,
    }
    return HttpResponse(template.render(context, request))


def add_images(request):
    dataset = request.POST['dataset']
    img_folder = request.POST['imgfolder']
    images = request.POST.getlist('imgs[]')

    images_dir = settings.BASE_IMAGES_PATH+'/'+img_folder
    datasets_dir = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS])

    current_dataset_ids = [int(os.path.splitext(f)[0]) for f in os.listdir(datasets_dir) if
                           os.path.isfile(os.path.join(datasets_dir, f))]

    if len(current_dataset_ids) > 0:
        data_id = current_dataset_ids[-1] + 1
    else:
        data_id = 1
    for image in images:
        data = {
            'image': images_dir + '/' + image
        }
        with open(datasets_dir+'/'+str(data_id) + '.json', 'w') as f:
            json.dump(data, f)
        data_id += 1

    response = {
        "success": True,
        "message": "Images added to dataset",
    }
    return JsonResponse(response)


def list_data(request):
    dataset = request.GET['dataset']
    datasets_info_dir = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS])
    datasets_annot_dir = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_ANNOTATIONS])
    info_files = [f for f in os.listdir(datasets_info_dir) if
                  os.path.isfile(os.path.join(datasets_info_dir, f))]

    annotations = []
    for info_file in info_files:
        with open(datasets_info_dir+'/'+info_file) as json_file:
            try:
                info_content = json.load(json_file)
                info_content['id'] = int(os.path.splitext(info_file)[0])
                info_content['is_annotated'] = os.path.exists(datasets_annot_dir+'/'+info_file)
                annotations.append(info_content)
            except:
                pass

    annotations = sorted(annotations, key=lambda i: (int(i['id'])))

    response = {
        "success": True,
        "message": "Data was successfully retrieved",
        "data": {
            "annotations": annotations
        }
    }
    return JsonResponse(response)


def remove_data(request):
    id = request.POST['id']
    dataset = request.POST['dataset']
    datasets_dir = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.DIR_DATASETS_INFOS])

    current_dataset_ids = [int(os.path.splitext(f)[0]) for f in os.listdir(datasets_dir) if
                           os.path.isfile(os.path.join(datasets_dir, f))]
    last_data_id = current_dataset_ids[-1]

    os.remove(datasets_dir + '/' + id + '.json')
    if str(last_data_id) == id:
        open(datasets_dir + '/' + id + '.json', 'w')

    response = {
        "success": True,
        "message": "Data was successfully removed",
    }
    return JsonResponse(response)