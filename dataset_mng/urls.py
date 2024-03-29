from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_dataset', views.create_dataset, name='create_dataset'),
    path('remove_dataset', views.remove_dataset, name='remove_dataset'),
    path('annot_mng', views.manage_annot, name='manage_annot'),
    path('add_images', views.add_images, name='add_images'),
    path('list_data', views.list_data, name='list_data'),
    path('remove_data', views.remove_data, name='remove_data'),
    #path('upload_file', views.upload_file, name='upload_file'),
    #path('remove_file', views.remove_file, name='remove_file'),
    path('export_mscoco', views.export_mscoco, name='export_mscoco'),
]