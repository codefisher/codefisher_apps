from django.conf.urls import patterns, url
from codefisher_apps.favicon_getter import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='ico-index'),
    url(r'^get_icons/', views.favicons, name='ico-get-favicons'),
    url(r'^favicon/', views.favicon, name='ico-favicons'),
)
