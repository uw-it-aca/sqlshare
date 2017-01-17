from django.conf.urls import include, url
from sqlshare_web.views import (dataset_detail, dataset_list,
                                dataset_list_page, dataset_permissions,
                                dataset_snapshot, dataset_upload,
                                dataset_upload_chunk, finalize_process,
                                logout, new_query, oauth_return,
                                patch_dataset_description,
                                patch_dataset_public, patch_dataset_sql,
                                query_status, query_status_page,
                                recent_queries, run_delete_dataset,
                                run_download, run_query, sharing_url,
                                upload_parser, user_search)



urlpatterns = [
    url(r'^$', dataset_list,
        {"list_type": "yours"}, name="dataset_list"),
    url(r'^shared$', dataset_list,
        {"list_type": "shared"}),
    url(r'^all$', dataset_list,
        {"list_type": "all"}),
    url(r'^recent$', dataset_list,
        {"list_type": "recent"}),

    url(r'^detail/(?P<owner>.*)/(?P<name>.*)/patch_sql',
        patch_dataset_sql),
    url(r'^detail/(?P<owner>.*)/(?P<name>.*)/patch_description',
        patch_dataset_description),
    url(r'^detail/(?P<owner>.*)/(?P<name>.*)/toggle_public',
        patch_dataset_public),
    url(r'^detail/(?P<owner>.*)/(?P<name>.*)/delete',
        run_delete_dataset),
    url(r'^detail/(?P<owner>.*)/(?P<name>.*)/permissions',
        dataset_permissions),

    url(r'^detail/(?P<owner>.*)/(?P<name>.*)$',
        dataset_detail,
        name='dataset_detail'),

    url(r'^snapshot/(?P<owner>.*)/(?P<name>.*)$',
        dataset_snapshot,
        name='make_dataset_snapshot'),


    url(r'^upload_chunk', dataset_upload_chunk,
        name='dataset_upload_chunk'),

    url(r'^upload/finalize_process/(?P<filename>.*)',
        finalize_process,
        name='upload_finalize_process'),

    url(r'^upload/parser/(?P<filename>.*)', upload_parser,
        name='upload_parser'),

    url(r'^upload', dataset_upload,
        name='dataset_upload'),
    url(r'^new', new_query, name="new_query"),
    url(r'^run_query', run_query, name="run_query"),
    url(r'^user_search/(?P<term>.*)', user_search),
    url(r'^queries$', recent_queries),
    url(r'^queries/(?P<query_id>.*)', query_status_page,
        name="query_status_page"),
    url(r'^query/(?P<query_id>.*)', query_status, name="query_status"),
    url(r'^dataset_list/next_page', dataset_list_page,
        name="dataset_list_page"),
    url(r'^run_download/', run_download),
    url(r'^oauth/', oauth_return),
    url(r'^logout', logout),
    url(r'^dataset/(?P<token>.*)', sharing_url),
]
