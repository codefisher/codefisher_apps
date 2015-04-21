from django.contrib import admin
from .models import ProxyPage

class ProxyPageAdmin(admin.ModelAdmin):
    list_display = ('path', 'proxy')
    list_filter = ('site',)
    search_fields = ('path', 'proxy')
    radio_fields = {'site': admin.VERTICAL}

admin.site.register(ProxyPage, ProxyPageAdmin)