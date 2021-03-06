from django.conf.urls import url
from codefisher_apps.downloads import views

urlpatterns = [
    url(r'^(?P<path>.*)/version/(?P<version>.*)$', views.release_notes, name='download-release-notes'),
    url(r'^download/(?P<path>.*)$', views.file_listing, name='download-file-listing'),
]