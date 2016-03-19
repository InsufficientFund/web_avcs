from . import views
from django.conf.urls import url
urlpatterns = [
    url(r'^upload/', views.upload, name='upload'),
    url(r'^$', views.index, name='index'),
]