from django.conf.urls import url
from . import views
from .views import EditSocialClass

from .views import user_filter
from .views import user_filter_dos

from .views import user_filter_tres
from .views import user_filter_cuatro

app_name = 'client'


urlpatterns = [
    #el \d+ indica que pk es numerica
    #url(r'^show/(?P<pk>\d+)/$', views.ShowView.as_view(), name='show'),
    #el \w+ indica que username es alfanumerico
    url(r'^show/(?P<username_url>\w+)/$', views.ShowView.as_view(), name='show'),
    #url(r'^show/$', views.show, name='show'),
    #url(r'^login/$', views.login, name='login'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    #url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/$', views.DashboardView.as_view(), name='dashboard'),
    #url(r'^create/$', views.create, name='create'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    #
    url(r'^edit/$', views.edit_client_unidos, name='edit'),
    url(r'^edit_password/$', views.edit_password, name='edit_password'),
    #
    #url(r'^edit/$', edit_client, name='edit'),
    #url(r'^edit_password/$', edit_password, name='edit_password'),
    url(r'^edit_social/$', EditSocialClass.as_view(), name='edit_social'),
    #
    url(r'^edit_client/$', views.edit_client, name='edit_client'),
    url(r'^edit_client_unidos/$', views.edit_client_unidos, name='edit_client_unidos'),

    url(r'filter/(?P<username>\w+)/$', user_filter, name='filter'),
    url(r'filterdos/(?P<username>\w+)/$', user_filter_dos, name='filterdos'),

    url(r'filtertres$', user_filter_tres, name='filtertres'),
    url(r'filtercuatro$', user_filter_cuatro, name='filtercuatro'),

]