import httplib2
import re
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect
from django.shortcuts import render
from djangopress.core.util import get_client_ip
from models import ProxyPage

class ProxyMiddleware(object):
    """This is for checking the old site, so to load pages from there """
    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a flatpage for non-404 responses.
        try:
            try:
                proxy = ProxyPage.objects.get(path=request.path, site_id=settings.SITE_ID)
                return self.proxy_page(request, proxy)
            except ProxyPage.DoesNotExist:
                try:
                    if request.path[-1] != '/':
                        ProxyPage.objects.get(path=request.path+'/', site_id=settings.SITE_ID)
                        #did not throw an exception, so lets redirect
                        return HttpResponsePermanentRedirect(request.path+'/')
                    else:
                        raise Http404
                except ProxyPage.DoesNotExist:
                    raise Http404
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response

    def proxy_page(self, request, proxy):
        conn = httplib2.Http()
        url = request.path
        headers = dict((header.lstrip('HTTP_'), value) for (header, value) 
           in request.META.items() if header.startswith('HTTP_'))
        headers["x-internal-from-new"] = "yes"
        headers["X-FORWARDED-FOR"] = get_client_ip(request)
        try:
            if request.method == 'POST':
                headers['Content-type'] = 'application/x-www-form-urlencoded'
                url = proxy.proxy + url
                data = request.POST.urlencode()
                response, content = conn.request(url, request.method, data, headers=headers)
            else:
                url_ending = '%s?%s' % (url, request.GET.urlencode())
                url = proxy.proxy + url_ending
                response, content = conn.request(url, request.method, headers=headers)
        except:
            raise Http404
        if int(response['status']) != 200:
            raise Http404
        if response.get("x-page-title"):
            m = re.search('<head>(.*)</head><body>(.*)</body>', content, flags=re.DOTALL)
            data = {"page_content": m.group(2), 
                    "title": response.get("x-page-title"), 'extra_head_content': m.group(1)}
            return render(request, "base.html", data)
        return HttpResponse(content, status=int(response['status']), content_type=response['content-type'])
    