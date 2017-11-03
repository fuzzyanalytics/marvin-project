from django.conf.urls import url

from mktdata import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^data/$', views.render_eurusd_mktdata, name='data'),
]
