from django.http import Http404
from django.conf import settings
import httplib2
from django.http import HttpResponse

PROXY_FORMAT = u'http://%s:%d%s' % ("127.0.0.1", "8081", u'%s')

class PagesMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a flatpage for non-404 responses.
        try:
            return proxy_page(request, request.path_info)
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
       
    if request.method == 'GET':
        url_ending = '%s?%s' % (url, request.GET.urlencode())
        url = PROXY_FORMAT % url_ending
        response, content = conn.request(url, request.method, headers={'x-internal-from-new':'yes'})
    elif request.method == 'POST':
        url = PROXY_FORMAT % url
        data = request.POST.urlencode()
        response, content = conn.request(url, request.method, data, headers={'x-internal-from-new':'yes'})
    if int(response['status']) == 404:
        raise Http404
    return HttpResponse(content, status=int(response['status']), mimetype=response['content-type'])