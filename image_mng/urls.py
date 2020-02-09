from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_folder', views.create_folder, name='create_folder'),
    path('remove_folder', views.remove_folder, name='remove_folder'),
    path('file_mng', views.manage_file, name='manage_file'),
    path('upload_file', views.upload_file, name='upload_file'),
    path('remove_file', views.remove_file, name='remove_file'),
]