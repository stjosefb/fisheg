from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_ref_dataset', views.create_ref_dataset, name='create_ref_dataset'),
    path('annot_mng', views.manage_annot, name='manage_annot'),
]