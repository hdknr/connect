from django.conf.urls import include, url     # patterns
from django.contrib import admin
admin.autodiscover()
#
# from issues.api import IssueResource
# from todos import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('connect.az.wellknowns')),
]

# urlpatterns = patterns(
#     '',
#     # Examples:
#     # url(r'^$', 'app.views.home', name='home'),
#     # url(r'^app/', include('app.foo.urls')),
#
#     # Uncomment the admin/doc line below to enable admin documentation:
#     # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
#
#     # Uncomment the next line to enable the admin:
#     url(r'^admin/', include(admin.site.urls)),
#     url(r'^connect/az/', include('connect.az.urls')),
#     url(r'^connect/rp/', include('connect.rp.urls')),
#     # url(r'^issues/api/', include(IssueResource().urls)),
#     url(r'', include('connect.az.wellknowns')),
#     url(r'', views.default, name="top"),
# )
