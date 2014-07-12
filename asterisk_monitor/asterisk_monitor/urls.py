from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from ast_rec.forms import AuthForm
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'asterisk_monitor.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^ast_rec/', include('ast_rec.urls', namespace="ast_rec")),
    url(r'^login$', login, {'template_name': 'ast_rec/login.html', 'authentication_form': AuthForm, 'extra_context': {'next': '/ast_rec'}}),
    url(r'^logout$', logout, {'next_page': '/login'})#, {'template_name': 'ast_rec/login.html', 'extra_context': {'next': '/ast_rec'}}),
)
