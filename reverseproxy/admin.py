from django.contrib import admin
from codefisher_apps.reverseproxy import ProxyPages

class ProxyPagesAdmin(admin.ModelAdmin):
    list_display = ('path', 'proxy')
    list_filter = ('site',)
    search_fields = ('path', 'proxy')
    radio_fields = {'site': admin.VERTICAL}

admin.site.register(ProxyPages, ProxyPagesAdmin)