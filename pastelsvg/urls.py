from django.conf.urls import patterns, url
from codefisher_apps.pastelsvg import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='pastel-svg-index'),
    url(r'^icon/(?P<file_name>.+)/$', views.icon, name='pastel-svg-icon'),
    url(r'^icon/$', views.list_icons, name='pastel-svg-icon'),
    url(r'^icon/page/(?P<page>\d+)$', views.list_icons, name='pastel-svg-icon'),
    url(r'^request/$', views.request_icon_list, name='pastel-svg-request'),
    url(r'^request/(?P<request_id>\d+)/$', views.request_icon, name='pastel-svg-request'),
    url(r'^request/(?P<request_id>\d+)/vote/$', views.request_icon_vote, name='pastel-svg-request-vote'),
    url(r'^request/(?P<request_id>\d+)/follow/$', views.request_icon_follow, name='pastel-svg-request-follow'),
    url(r'^request/page/(?P<page>\d+)/$', views.request_icon_list, name='pastel-svg-request'),
    url(r'^request/make/$', views.make_icon_request, name='pastel-svg-request-make'),
    url(r'^request/vote/(?P<request_id>\d+)/$', views.request_icon_vote, name='pastel-svg-request-vote'),
    url(r'^request/vote/(?P<request_id>\d+)/ajax/$', views.request_icon_vote_ajax, name='pastel-svg-request-vote-ajax'),
    url(r'^donate/$', views.donate, name='pastel-svg-donate'),
    url(r'^download/$', views.download, name='pastel-svg-download'),
    url(r'^download_file/(?P<file>\d+)/(?P<file_name>.+)$', views.download_file, name='pastel-svg-download-file'),
    url(r'^donate/thanks/$', views.donate_thanks, name='pastel-svg-donate-thanks'),
    url(r'^who_uses/$', views.who_uses, name='pastel-svg-who-uses'),
    url(r'^who_uses/(?P<page>\d+)/$', views.who_uses, name='pastel-svg-who-uses'),
)

try:
    from djangopress.core.search import ModelSetSearchForm, ModelSetSearchView, search_view_factory

    urlpatterns += patterns('',
        # the haystack search
        url(r'^search/', search_view_factory(
                view_class=ModelSetSearchView,
                form_class=ModelSetSearchForm,
                results_per_page=20,
                template='pastelsvg/search.html',
                models=["pastelsvg.icon"],
            ), name='haystack-pastelsvg-search'),
    )
except ImportError:
    pass