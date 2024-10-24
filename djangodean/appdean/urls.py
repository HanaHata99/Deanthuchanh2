from django.urls import path
from . import views

urlpatterns = [
    path('trangchu/', views.trangchu, name='trangchu'),
    path('', views.trangchu, name='trangchu'),
]