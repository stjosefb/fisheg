from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
import json
import os
import shutil
from fisheg import settings
import time


def index(request):
    error = ''

    # params
    message = ''
    if 'message' in request.GET:
        message = request.GET['message']
    dataset = ''
    if 'dataset' in request.GET:
        dataset = request.GET['dataset']

    # data
    classes = []
    dataset_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.FILENAME_DATASET_INFO])
    try:
        with open(dataset_info_file) as json_file:
            try:
                info_content = json.load(json_file)
                classes = info_content['classes']
            except Exception as e:
                error = str(e)
                pass
    except Exception as e:
        pass

    # content
    template = loader.get_template('class_mng/index.html')
    context = {
        'class_list': classes,
        'dataset': dataset,
        'message': message,
        'error': error
    }
    return HttpResponse(template.render(context, request))


def remove_class(request):
    try:
        # params
        dataset = request.POST['dataset']
        class_id = request.POST['class_id']

        # info file
        dataset_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.FILENAME_DATASET_INFO])

        # load data
        info_content = None
        with open(dataset_info_file, 'r') as json_file:
            try:
                info_content = json.load(json_file)
            except Exception as e:
                error = str(e)
                pass

        # modify
        info_content['classes'] = [x for x in info_content['classes'] if str(x['id']) != class_id]
        for idx, class_ in enumerate(info_content['classes']):
            class_['id'] = idx+1

        # save
        os.remove(dataset_info_file)
        with open(dataset_info_file, 'w') as f:
            json.dump(info_content, f, indent=4)


    except OSError:
        #pass
        message = 'Failed'
        #print("Creation of the directory %s failed" % path)
    else:
        #pass
        message = 'Successful'
        #print("Successfully created the directory %s " % path)
    return HttpResponseRedirect('.'+'?dataset='+dataset+'&message='+message)


def create_class(request):
    try:
        # params
        dataset = request.POST['dataset']
        class_name = request.POST['class_name']
        class_color = request.POST['class_color']

        # info file
        dataset_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.FILENAME_DATASET_INFO])

        # load data
        info_content = None
        if os.path.exists(dataset_info_file):
            with open(dataset_info_file, 'r') as json_file:
                try:
                    info_content = json.load(json_file)

                except Exception as e:
                    error = str(e)
                    pass

        # init info_content if file not exist
        if info_content is None:
            info_content = {'classes': []}

        # modify
        new_class = {'id': len(info_content['classes'])+1, 'name': class_name, 'color': class_color}
        info_content['classes'].append(new_class)

        # save
        if os.path.exists(dataset_info_file):
            os.remove(dataset_info_file)
        with open(dataset_info_file, 'w') as f:
            json.dump(info_content, f, indent=4)

    except OSError as e:
        #pass
        message = 'Failed '+str(e)
        #print("Creation of the directory %s failed" % path)
    else:
        #pass
        message = 'Successful'
        #print("Successfully created the directory %s " % path)
    return HttpResponseRedirect('.'+'?dataset='+dataset+'&message='+message)
    #return HttpResponse(folder)


def update_class(request):
    try:
        # params
        dataset = request.POST['dataset']
        class_id = request.POST['class_id']
        class_name = request.POST['class_name']
        class_color = request.POST['class_color']

        # info file
        dataset_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.FILENAME_DATASET_INFO])

        # load data
        info_content = None
        if os.path.exists(dataset_info_file):
            with open(dataset_info_file, 'r') as json_file:
                try:
                    info_content = json.load(json_file)

                except Exception as e:
                    error = str(e)
                    pass

        # init info_content if file not exist
        if info_content is None:
            info_content = {'classes': []}

        # modify
        for class_ in info_content['classes']:
            if str(class_['id']) == class_id:
                class_['name'] = class_name
                class_['color'] = class_color
                break

        # save
        if os.path.exists(dataset_info_file):
            os.remove(dataset_info_file)
        with open(dataset_info_file, 'w') as f:
            json.dump(info_content, f, indent=4)

    except OSError as e:
        #pass
        message = 'Failed '+str(e)
        #print("Creation of the directory %s failed" % path)
    else:
        #pass
        message = 'Successful'
        #print("Successfully created the directory %s " % path)
    return HttpResponseRedirect('.'+'?dataset='+dataset+'&message='+message)
    #return HttpResponse(folder)
