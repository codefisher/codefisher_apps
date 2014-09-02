from django.conf.urls import patterns, url
from codefisher_apps.svn_xslt import views

urlpatterns = patterns('',
    url(r'^style.xslt$', views.xslt),
)
