from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^response$', views.auto_response, name='auto_response'),
    url(r'^response_api$', views.response_api, name='response_api'),
    url(r'^login/staff/$', views.login_page, name='login_page'),
    url(r'^page/counsellor/$', views.counsellor, name='counsellor'),
    url(r'^page/supervisor/$', views.supervisor, name='supervisor'),
    url(r'^page/administrator/$', views.administrator, name='administrator'),
    url(r'^page/staffstatus/$', views.staffstatus, name='staffstatus'),
    url(r'^api/getseq/$', views.getseq, name='getseq'),
    url(r'^api/addstud/$', views.addstud, name='addstud'),
    url(r'^api/getstud/$', views.getstud, name='getstud'),
    url(r'^api/deletestud/$', views.deletestud, name='deletestud'),
    url(r'^api/updatestud/$', views.updatestud, name='updatestud'),
    url(r'^api/getstafflist/$', views.getstafflist, name='getstafflist'),
    url(r'^api/getstaff/$', views.getstaff, name='getstaff'),
    url(r'^api/addstaff/$', views.addstaff, name='addstaff'),
    url(r'^api/updatestaff/$', views.updatestaff, name='updatestaff'),
    url(r'^api/deletestaff/$', views.deletestaff, name='deletestaff'),
    url(r'^api/assignstaff/$', views.assignstaff, name='assignstaff'),
    url(r'^api/startchat/$', views.startchat, name='stratchat'),
    url(r'^api/endchat/$', views.endchat, name='endchat'),
    url(r'^user/login/$', views.login, name='login'),
    url(r'^user/login-sso/$', views.login_sso, name='login_sso'),
    url(r'^user/login-sso/callback/$', views.login_sso_callback, name='login_sso_callback'),
]
