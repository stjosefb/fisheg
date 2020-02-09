from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_dataset', views.create_dataset, name='create_dataset'),
    #path('remove_folder', views.remove_folder, name='remove_folder'),
    path('annot_mng', views.manage_annot, name='manage_annot'),
    #path('upload_file', views.upload_file, name='upload_file'),
    #path('remove_file', views.remove_file, name='remove_file'),
]