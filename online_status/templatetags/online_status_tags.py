import datetime

from django.conf import settings

from django import template
from django.core.cache import cache
from online_status.status import CACHE_USERS, CACHE_PREFIX_ANONYM_USER, TIME_OFFLINE, ONLY_LOGGED_USERS, status_for_user
from django.contrib.sessions.models import Session
    
register = template.Library()


@register.inclusion_tag('online_status/online_users_list.html')
def online_users(limit=None):
    return _online_user(limit, True)

@register.inclusion_tag('online_status/online_users_count.html')
def online_user_count(limit=None):
    data = _online_user(limit, False)
    return {'onlineanonymusers': len(data.get('onlineanonymusers')),
            'onlineusers': len(data.get('onlineusers')),}

def _online_user(limit, logged_only):
    """Renders a list of OnlineStatus instances"""
    onlineusers = cache.get(CACHE_USERS, [])
    onlineanonymusers = []

    if not ONLY_LOGGED_USERS and not logged_only:
        now = datetime.datetime.now()
        sessions = Session.objects.filter(expire_date__gte = now + datetime.timedelta(0, settings.SESSION_COOKIE_AGE - TIME_OFFLINE)).values_list('session_key', flat = True)
        onlineanonymusers = [x for x in [cache.get(CACHE_PREFIX_ANONYM_USER % session_key, None) for session_key in sessions] if x is not None]
        onlineusers = [item for item in cache.get(CACHE_USERS, []) if item.status in (0, 1) and item.session in sessions]
        
        if onlineanonymusers and limit:
            onlineanonymusers = onlineanonymusers[:limit]
            
    if onlineusers and limit:
        onlineusers = onlineusers[:limit]
    return {'onlineanonymusers': onlineanonymusers,
            'onlineusers': onlineusers,}


@register.inclusion_tag('online_status/user_status.html')
def user_status(user):
    """Renders an OnlineStatus instance for User"""
    status = status_for_user(user)
    return {'onlinestatus': status,}

@register.inclusion_tag('online_status/user_status_tag.html')
def user_status_tag(user):
    status = status_for_user(user)
    return {'onlinestatus': status,}