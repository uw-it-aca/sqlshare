from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^$', 'sqlshare_web.views.dataset_list',
        {"list_type": "yours"}, name="dataset_list"),
    url(r'^shared$', 'sqlshare_web.views.dataset_list',
        {"list_type": "shared"}),
    url(r'^all$', 'sqlshare_web.views.dataset_list',
        {"list_type": "all"}),
    url(r'^recent$', 'sqlshare_web.views.dataset_list',
        {"list_type": "recent"}),

    url(r'^detail/(?P<owner>.*)/(?P<name>.*)/patch_sql',
        'sqlshare_web.views.patch_dataset_sql'),
    url(r'^detail/(?P<owner>.*)/(?P<name>.*)/patch_description',
        'sqlshare_web.views.patch_dataset_description'),
    url(r'^detail/(?P<owner>.*)/(?P<name>.*)/toggle_public',
        'sqlshare_web.views.patch_dataset_public'),
    url(r'^detail/(?P<owner>.*)/(?P<name>.*)/delete',
        'sqlshare_web.views.run_delete_dataset'),
    url(r'^detail/(?P<owner>.*)/(?P<name>.*)/permissions',
        'sqlshare_web.views.dataset_permissions'),

    url(r'^detail/(?P<owner>.*)/(?P<name>.*)$',
        'sqlshare_web.views.dataset_detail',
        name='dataset_detail'),

    url(r'^snapshot/(?P<owner>.*)/(?P<name>.*)$',
        'sqlshare_web.views.dataset_snapshot',
        name='make_dataset_snapshot'),


    url(r'^upload_chunk', 'sqlshare_web.views.dataset_upload_chunk',
        name='dataset_upload_chunk'),

    url(r'^upload/finalize_process/(?P<filename>.*)',
        'sqlshare_web.views.finalize_process',
        name='upload_finalize_process'),

    url(r'^upload/parser/(?P<filename>.*)', 'sqlshare_web.views.upload_parser',
        name='upload_parser'),

    url(r'^upload', 'sqlshare_web.views.dataset_upload',
        name='dataset_upload'),
    url(r'^new/', 'sqlshare_web.views.new_query'),
    url(r'^run_query/', 'sqlshare_web.views.run_query'),
    url(r'^user_search/(?P<term>.*)', 'sqlshare_web.views.user_search'),
    url(r'^query/(?P<query_id>.*)', 'sqlshare_web.views.query_status'),
    url(r'^dataset_list/next_page', 'sqlshare_web.views.dataset_list_page'),
    url(r'^run_download/', 'sqlshare_web.views.run_download'),
    url(r'^download/(?P<query_id>[0-9]+)/download/(?P<token>[a-z0-9]+)',
        'sqlshare_web.views.download_status'),
    url(r'^oauth/', 'sqlshare_web.views.oauth_return'),

)
