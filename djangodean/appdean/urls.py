from django.urls import path
from . import views

urlpatterns = [
    path('listview/', views.listview, name='listview'),
    path('analysis/', views.analysis, name='analysis'),
    path('', views.listview, name='listview'),
    path('detailview/', views.detailview, name='detailview'),
    path('add_data/', views.add_data_view, name='add_data'),
    path('add_manual_data/', views.add_manual_data, name='add_manual_data'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('api/add-manual-data/', views.add_manual_data_api, name='add_manual_data_api'),
    path('api/upload-file/', views.UploadFileAPIView.as_view(), name='upload_file_api'),
]

