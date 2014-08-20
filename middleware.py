from django.http import Http404
from django.conf import settings
import httplib2
from django.http import HttpResponse
from django.shortcuts import render
import re

PROXY_FORMAT = u'http://%s:%d%s' % ("127.0.0.1", 8081, u'%s')

class PagesMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a flatpage for non-404 responses.
        try:
            return proxy_page(request)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response

def proxy_page(request):
    conn = httplib2.Http()
    url = request.path
    headers = dict((header.lstrip('HTTP_'), value) for (header, value) 
       in request.META.items() if header.startswith('HTTP_'))
    headers["x-internal-from-new"] = "yes"
    try:
        if request.method == 'GET':
            url_ending = '%s?%s' % (url, request.GET.urlencode())
            url = PROXY_FORMAT % url_ending
            response, content = conn.request(url, request.method, headers=headers)
        elif request.method == 'POST':
            headers['Content-type'] = 'application/x-www-form-urlencoded'
            url = PROXY_FORMAT % url
            data = request.POST.urlencode()
            response, content = conn.request(url, request.method, data, headers=headers)
    except:
        raise Http404
    if int(response['status']) == 404:
        raise Http404
    if response.get("x-page-title"):
        m = re.search('<head>(.*)</head><body>(.*)</body>', content, flags=re.DOTALL)
        data = {"page_content": m.group(1), 
                "title": response.get("x-page-title"), 'extra_head_content': m.group(1)}
        return render(request, "base.html", data)
    return HttpResponse(content, status=int(response['status']), mimetype=response['content-type'])
