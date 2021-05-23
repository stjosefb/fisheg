from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('save', views.save, name='save'),
    path('check_score', views.check_score, name='check_score'),
    path('upload_segmask_file', views.upload_segmask_file, name='upload_segmask_file'),
    path('grow_refine_traces', views.grow_refine_traces, name='grow_refine_traces'),
    path('init_anns_superpixel', views.init_anns_superpixel, name='init_anns_superpixel'),
]