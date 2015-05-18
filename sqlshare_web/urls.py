from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^$', 'sqlshare_web.views.dataset_list', name='dataset_list'),
    url(r'^detail/(?P<owner>.*)/(?P<name>.*)$',
        'sqlshare_web.views.dataset_detail',
        name='dataset_detail'),
    url(r'^upload', 'sqlshare_web.views.dataset_upload',
        name='dataset_upload'),
    url(r'^new/', 'sqlshare_web.views.new_query'),
    url(r'^oauth/', 'sqlshare_web.views.oauth_return'),
    
)
