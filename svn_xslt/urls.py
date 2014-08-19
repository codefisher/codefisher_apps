from django.conf.urls import patterns, url, include

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('codefisher_apps.svn_xslt.views',
    url(r'^style.xslt$', 'xslt'),
)
