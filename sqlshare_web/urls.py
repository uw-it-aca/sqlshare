from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^$', 'sqlshare_web.views.dataset_list', name='dataset_list'),
    url(r'^detail', 'sqlshare_web.views.dataset_detail',
        name='dataset_detail'),
    url(r'^upload', 'sqlshare_web.views.dataset_upload',
        name='dataset_upload'),
)
