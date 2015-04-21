import zlib
from django.middleware.cache import UpdateCacheMiddleware
from django.utils.cache import patch_response_headers, get_max_age, has_vary_header
from django.core.cache import cache
import collections

class UpdateCacheMiddlewareSimpleKey(UpdateCacheMiddleware):
    """
    Response-phase cache middleware that updates the cache if the response is
    cacheable.

    Must be used as part of the two-part update/fetch cache middleware.
    UpdateCacheMiddleware must be the first piece of middleware in
    MIDDLEWARE_CLASSES so that it'll get called last during the response phase.
    
    THIS IS A PATCHED VERSION OF WHAT IS IN DJANGO TO NGINX CAN GET THE PAGES OUT EASY
    """

    def process_response(self, request, response):
        """Sets the cache, if needed."""
        #if not self._should_update_cache(request, response):
        #    # We don't need to update the cache, just return.
        #    return response

        if response.streaming or response.status_code != 200:
            return response
        
        # Don't cache responses that set a user-specific (and maybe security
        # sensitive) cookie in response to a cookie-less request.
        if not request.COOKIES and response.cookies and has_vary_header(response, 'Cookie'):
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
            #raise ValueError(cache_key)
            if hasattr(response, 'render') and isinstance(response.render, collections.Callable):
                response.add_post_render_callback(
                    lambda r: cache._cache.set(cache_key.encode("utf-8"), zlib.compress(r.content, 9), timeout)
                )
            else:
                # we use the highest compression level, because since it is cached we hope for it to pay off
                cache._cache.set(cache_key.encode("utf-8"), zlib.compress(response.content, 9), timeout)
        return response
