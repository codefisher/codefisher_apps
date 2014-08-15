from django.conf.urls import patterns, url

urlpatterns = patterns('codefisher_apps.downloads.views',
    url(r'^(?P<path>.*)/version/(?P<version>.*)$', 'release_notes', name='download-release-notes'),
    url(r'^(?P<path>.*)$', 'file_listing', name='download-file-listing'),
)