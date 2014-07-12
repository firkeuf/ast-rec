from django.conf.urls import patterns, url
from django.conf import settings
import views

urlpatterns = patterns('',
                       url(r'^$', views.call_list_view, name='call_list_view'),
                       url(r'^sc$', views.synchronous_calls, name='synchronous_calls'),
                       url(r'^bhc$', views.by_hour_calls, name='by_hour_calls'),
                       url(r'^records/(?P<uniqueid>\w+)$', views.records_xsendfile,
                           {'document_root': settings.RECORDS_ROOT, }, name='records_xsendfile'),

                       # url(r'^vote/$', views.vote, name='vote'),
)