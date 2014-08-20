from django.http import Http404
from django.conf import settings
import httplib2
from django.http import HttpResponse
from django.shortcuts import render
import re
from django.core.cache import cache
from django.utils.cache import patch_response_headers, get_max_age

class PagesMiddleware(object):
    """This is for checking the old site, so to load pages from there """
    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a flatpage for non-404 responses.
        try:
            return self.proxy_page(request)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response

    def proxy_page(self, request):
        conn = httplib2.Http()
        url = request.path
        headers = dict((header.lstrip('HTTP_'), value) for (header, value) 
           in request.META.items() if header.startswith('HTTP_'))
        headers["x-internal-from-new"] = "yes"
        try:
            if request.method == 'GET':
                url_ending = '%s?%s' % (url, request.GET.urlencode())
                url = settings.PROXY_FORMAT % url_ending
                response, content = conn.request(url, request.method, headers=headers)
            elif request.method == 'POST':
                headers['Content-type'] = 'application/x-www-form-urlencoded'
                url = settings.PROXY_FORMAT % url
                data = request.POST.urlencode()
                response, content = conn.request(url, request.method, data, headers=headers)
        except:
            raise Http404
        if int(response['status']) == 404:
            raise Http404
        if response.get("x-page-title"):
            m = re.search('<head>(.*)</head><body>(.*)</body>', content, flags=re.DOTALL)
            data = {"page_content": m.group(2), 
                    "title": response.get("x-page-title"), 'extra_head_content': m.group(1)}
            return render(request, "base.html", data)
        return HttpResponse(content, status=int(response['status']), mimetype=response['content-type'])
    
    
class UpdateCacheMiddleware(object):
    """
    Response-phase cache middleware that updates the cache if the response is
    cacheable.

    Must be used as part of the two-part update/fetch cache middleware.
    UpdateCacheMiddleware must be the first piece of middleware in
    MIDDLEWARE_CLASSES so that it'll get called last during the response phase.
    
    THIS IS A PATCHED VERSION OF WHAT IS IN DJANGO TO NGINX CAN GET THE PAGES OUT EASY
    """
    def __init__(self):
        self.cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.cache_anonymous_only = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)

    def process_response(self, request, response):
        """Sets the cache, if needed."""
        if not hasattr(request, '_cache_update_cache') or not request._cache_update_cache:
            # We don't need to update the cache, just return.
            return response
        if request.method != 'GET':
            # This is a stronger requirement than above. It is needed
            # because of interactions between this middleware and the
            # HTTPMiddleware, which throws the body of a HEAD-request
            # away before this middleware gets a chance to cache it.
            return response
        if not response.status_code == 200:
            return response
        # Try to get the timeout from the "max-age" section of the "Cache-
        # Control" header before reverting to using the default cache_timeout
        # length.
        timeout = get_max_age(response)
        if timeout == None:
            timeout = self.cache_timeout
        elif timeout == 0:
            # max-age was set to 0, don't bother caching.
            return response
        patch_response_headers(response, timeout)
        if timeout:
            cache_key = "%s-%s" % (self.key_prefix, request.get_full_path())
            cache.set(cache_key, response, timeout)
        return response
