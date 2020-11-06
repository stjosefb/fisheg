from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_class', views.create_class, name='create_class'),
    path('update_class', views.update_class, name='update_class'),
    path('remove_class', views.remove_class, name='remove_class'),
]