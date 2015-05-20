from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include('sqlshare_rest.urls')),
#    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^accounts/login/$', 'sqlshare_rest.views.auth.wayf'),
    url(r'^admin/', include(admin.site.urls)),
)

from oauth2_provider import views as oa_views
oauth_app_patterns = patterns(
    '',
    url(r'^applications/$', oa_views.ApplicationList.as_view(), name="list"),
    url(r'^applications/register/$', oa_views.ApplicationRegistration.as_view(), name="register"),
    url(r'^applications/(?P<pk>\d+)/$', oa_views.ApplicationDetail.as_view(), name="detail"),
    url(r'^applications/(?P<pk>\d+)/delete/$', oa_views.ApplicationDelete.as_view(), name="delete"),
    url(r'^applications/(?P<pk>\d+)/update/$', oa_views.ApplicationUpdate.as_view(), name="update"),
)
