from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import os
import time
from fisheg import settings


BASE_IMAGES_PATH = 'media/images'


def index(request):
    #return HttpResponse("Hello, world. You're at the main index.")
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    #output = ', '.join([q.question_text for q in latest_question_list])
    #return HttpResponse(output)
    message = ''
    if 'message' in request.GET:
        message = request.GET['message']
    template = loader.get_template('image_mng/index.html')
    subfolders = [f.name for f in os.scandir(BASE_IMAGES_PATH) if f.is_dir()]
    context = {
        'folder_list': subfolders,
        'message': message
    }
    return HttpResponse(template.render(context, request))


def create_folder(request):
    try:
        folder = request.POST['new_folder']
        #print(folder)
        os.mkdir(BASE_IMAGES_PATH+'/'+folder)
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


def remove_folder(request):
    try:
        folder = request.POST['folder']
        #print(folder)
        os.rmdir(BASE_IMAGES_PATH+'/'+folder)
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


def manage_file(request):
    message = ''
    if 'message' in request.GET:
        message = request.GET['message']
    template = loader.get_template('image_mng/file_mng.html')
    folder = request.GET['folder']
    files = [f.name for f in os.scandir(BASE_IMAGES_PATH+'/'+folder)]
    #a = settings.MEDIA_ROOT
    context = {
        'file_list': files,
        'folder': folder,
        'message': message,
        'ts': time.time()
    }
    return HttpResponse(template.render(context, request))


def upload_file(request):
    folder = request.POST['folder']
    if 'new_file' in request.FILES:
        try:
            #pass
            #print(folder)
            #os.rmdir(BASE_IMAGES_PATH+'/'+folder)

            f = request.FILES['new_file']
            filename = request.FILES['new_file'].name
            if os.path.isfile('/'.join([BASE_IMAGES_PATH, folder, filename])):
                name_ext_tup = os.path.splitext(filename)
                filename = name_ext_tup[0]+' (2)'+name_ext_tup[1]
            with open('/'.join([BASE_IMAGES_PATH, folder, filename]), 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
        except OSError:
            #pass
            message = 'Failed'
        else:
            #pass
            message = 'Successful'
    else:
        message = 'No file uploaded'
    return HttpResponseRedirect('file_mng' + '?folder='+folder+'&message=' + message)


def remove_file(request):
    try:
        folder = request.POST['folder']
        file = request.POST['file']
        #print(folder)
        os.remove('/'.join([BASE_IMAGES_PATH, folder, file]))
    except OSError:
        #pass
        message = 'Failed'
        #print("Creation of the directory %s failed" % path)
    else:
        #pass
        message = 'Successful'
        #print("Successfully created the directory %s " % path)
    return HttpResponseRedirect('file_mng' + '?folder='+folder+'&message=' + message)
    #return HttpResponse(folder)
