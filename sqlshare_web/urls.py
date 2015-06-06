from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^$', 'sqlshare_web.views.dataset_list', name='dataset_list'),
    url(r'^detail/(?P<owner>.*)/(?P<name>.*)$',
        'sqlshare_web.views.dataset_detail',
        name='dataset_detail'),

    url(r'^upload_chunk', 'sqlshare_web.views.dataset_upload_chunk',
        name='dataset_upload_chunk'),

    url(r'^upload/finalize_process/(?P<filename>.*)',
        'sqlshare_web.views.finalize_process',
        name='upload_finalize_process'),


    url(r'^upload/finalize/(?P<filename>.*)',
        'sqlshare_web.views.upload_finalize',
        name='upload_finalize'),

    url(r'^upload/parser/(?P<filename>.*)', 'sqlshare_web.views.upload_parser',
        name='upload_parser'),

    url(r'^upload', 'sqlshare_web.views.dataset_upload',
        name='dataset_upload'),
    url(r'^new/', 'sqlshare_web.views.new_query'),
    url(r'^run_query/', 'sqlshare_web.views.run_query'),
    url(r'^query/(?P<query_id>.*)', 'sqlshare_web.views.query_status'),
    url(r'^run_download/', 'sqlshare_web.views.run_download'),
    url(r'^download/(?P<query_id>[0-9]+)/download/(?P<token>[a-z0-9]+)',
        'sqlshare_web.views.download_status'),
    url(r'^oauth/', 'sqlshare_web.views.oauth_return'),
)
