from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()
#
from issues.api import IssueResource

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'app.views.home', name='home'),
    # url(r'^app/', include('app.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^connect/az/', include('connect.az.urls')),
    url(r'issues/api/', include(IssueResource().urls)),
    url(r'', include('connect.api.wellknowns')),
)
#
#from django.conf import settings
#if settings.DEBUG:
#    urlpatterns += patterns('',
#
#        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
#            'document_root': settings.STATIC_ROOT,
#            'show_indexes': True,
#        }),
#        url(r'^(?P<path>favicon.+)$', 'django.views.static.serve', {
#            'document_root': settings.STATIC_ROOT,
#            'show_indexes': True,
#        }),
#   )
#
