from django.urls import path
from . import views

urlpatterns = [
    path('listview/', views.listview, name='listview'),
    path('', views.listview, name='listview'),
    path('detailview/', views.detailview, name='detailview'),
]

