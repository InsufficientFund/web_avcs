from . import views
from django.conf.urls import url
urlpatterns = [
    url(r'^upload/', views.upload, name='upload'),
    url(r'^train_page/', views.train_page, name='train_page'),
    url(r'^predict_page/', views.predict_page, name='predict_page'),
    url(r'^get_sample_frame/', views.get_sample_frame, name='get_sample_frame'),
    url(r'^select_video/', views.select_video, name='select_video'),
    url(r'^train/', views.train, name='train'),
    url(r'^detect/', views.detect, name='detect'),
    url(r'^imp_data/', views.improve_data, name='improve_data'),
    url(r'^predict/', views.predict, name='predict'),
    url(r'^$', views.index, name='index'),
]