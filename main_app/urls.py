from . import views
from django.conf.urls import url
urlpatterns = [
    url(r'^upload/', views.upload, name='upload'),
    url(r'^test_api/', views.test_api, name='test_api'),
    url(r'^$', views.index, name='index'),
]