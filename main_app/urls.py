from . import views
from django.conf.urls import url
urlpatterns = [
    url(r'^upload/', views.upload, name='upload'),
    url(r'^train_page/', views.train_page, name='train_page'),
    url(r'^predict_page/get_graph_data/', views.get_graph_data, name='get_graph_data'),
    url(r'^predict_page/get_line_data/', views.get_line_data, name='get_line_data'),
    url(r'^predict_page/get_progress_data/', views.get_progress_data, name='get_progress_data'),
    url(r'^predict_page/', views.predict_page, name='predict_page'),
    url(r'^get_sample_frame/', views.get_sample_frame, name='get_sample_frame'),
    url(r'^select_video/', views.select_video, name='select_video'),
    url(r'^train/', views.train, name='train'),
    url(r'^detect/', views.detect, name='detect'),
    url(r'^imp_data/', views.improve_data, name='improve_data'),
    url(r'^predict/', views.predict, name='predict'),
    url(r'^resend/', views.resend_data, name='resend_data'),
    url(r'^search_res/', views.search_res, name='search_res'),
    url(r'^send_result/', views.send_result, name='send_result'),
    url(r'^login/', views.login_view, name='login_view'),
    url(r'^logout/', views.logout_session, name='logout_session'),
    url(r'^auth/', views.auth_and_login, name='auth_and_login'),
    url(r'^result_image/', views.result_image, name='result_image'),
    url(r'^chgpwd_opt/', views.change_password, name='change_password'),
    url(r'^chgpwd/', views.change_password_view, name='change_password_view'),
    url(r'^upload_train/', views.upload_train, name='upload_train'),
    url(r'^$', views.index, name='index'),

]
