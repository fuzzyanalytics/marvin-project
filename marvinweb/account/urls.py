from django.conf.urls import url, include

urlpatterns = [
    # url(r'login/$', views.user_login, name='login'),
    # url(r'^$', views.dashboard, name='dashboard'),
    url('^', include('django.contrib.auth.urls')),
    # login / logout urls
    # url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    # url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    # url(r'^logout-then-login/$',auth_views.logout_then_login, name='logoutthenlogin'),
]



# include('django.contrib.auth.urls') includes the following URL patterns
# ^login/$ [name='login']
# ^logout/$ [name='logout']
# ^password_change/$ [name='password_change']
# ^password_change/done/$ [name='password_change_done']
# ^password_reset/$ [name='password_reset']
# ^password_reset/done/$ [name='password_reset_done']
# ^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$ [name='password_reset_confirm']
# ^reset/done/$ [name='password_reset_complete']
