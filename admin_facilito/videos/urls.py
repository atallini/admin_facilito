from django.conf.urls import url
from .views import ListVideo
from .views import DetailVideo

app_name = 'videos'

urlpatterns = [
    #el \d+ indica que pk es numerica
    #url(r'^show/(?P<pk>\d+)/$', views.ShowView.as_view(), name='show'),
    #el \w+ indica que username es alfanumerico

    url(r'^videos/$', ListVideo.as_view(), name='lista-video'),
    url(r'^videos/(?P<pk>[0-9]+)$', DetailVideo.as_view(), name='detail-video'),

]