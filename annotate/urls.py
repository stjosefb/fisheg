from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('save', views.save, name='save'),
    path('check_score', views.check_score, name='check_score'),
    path('upload_segmask_file', views.upload_segmask_file, name='upload_segmask_file'),
]