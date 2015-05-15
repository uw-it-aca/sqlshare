from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^$', 'sqlshare_web.views.dataset_list', name='dataset_list'),
    url(r'^detail/(?P<owner>.*)/(?P<name>.*)$',
        'sqlshare_web.views.dataset_detail',
        name='dataset_detail'),

    url(r'^upload_chunk', 'sqlshare_web.views.dataset_upload_chunk',
        name='dataset_upload_chunk'),

    url(r'^upload/parser/(?P<filename>.*)', 'sqlshare_web.views.upload_parser',
        name='upload_parser'),

    url(r'^upload', 'sqlshare_web.views.dataset_upload',
        name='dataset_upload'),



    url(r'^oauth/', 'sqlshare_web.views.oauth_return'),
)
