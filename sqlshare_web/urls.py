from django.conf.urls import patterns, include, url

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    
    # url(r'^blog/', include('blog.urls')),
    #url(r'^admin/', include(admin.site.urls)),
    
    # include applications
    url(r'^$', 'sqlshare_web.views.dataset_list', name='dataset_list'),
    url(r'^detail', 'sqlshare_web.views.dataset_detail', name='dataset_detail'),
    url(r'^upload', 'sqlshare_web.views.dataset_upload', name='dataset_upload'),
)
