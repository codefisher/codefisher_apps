from django.conf.urls import url
from codefisher_apps.svn_xslt import views

urlpatterns = [
    url(r'^style.xslt$', views.xslt),
]
