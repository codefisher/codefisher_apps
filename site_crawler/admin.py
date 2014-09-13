from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from codefisher_apps.site_crawler.models import CrawlProcess, CrawledPage, SpelledPage
from django import forms

def page_url(obj):
    return '<a href="%s">%s</a>' % (obj.url, obj.url)
page_url.allow_tags = True

class CrawlProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'crawler')
admin.site.register(CrawlProcess, CrawlProcessAdmin)

class StatusCodeFilter(SimpleListFilter):
    title = 'status_code'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return [(page['status'], page['status']) for page in CrawledPage.objects.order_by().values('status').distinct()]
        
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        
class ProcessFilter(SimpleListFilter):
    title = 'process'
    parameter_name = 'process'
    
    def lookups(self, request, model_admin):
        return [(page['process'], CrawlProcess.objects.get(pk=page['process']).name) for page in CrawledPage.objects.order_by().values('process').distinct()]
        
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(process=self.value())

class CrawledPageAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = CrawledPage
        widgets = {
          'url': forms.TextInput
        }
        
class CrawledPageAdmin(admin.ModelAdmin):
    list_display = ('url', 'page_title', 'status')
    list_filter = [StatusCodeFilter, ProcessFilter]
    form = CrawledPageAdminForm
    
    def page_title(self, obj):
        if not obj.title:
            return ''
        return obj.title
    
admin.site.register(CrawledPage, CrawledPageAdmin)

class ProcessSpellFilter(SimpleListFilter):
    title = 'process'
    parameter_name = 'process'
    
    def lookups(self, request, model_admin):
        return [(page['process'], CrawlProcess.objects.get(pk=page['process']).name) for page in SpelledPage.objects.order_by().values('process').distinct()]
        
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(process=self.value())

class SpelledPageAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = SpelledPage
        widgets = {
          'url': forms.TextInput
        }
        
class SpelledPageAdmin(admin.ModelAdmin):
    list_display = ('url', 'mistakes', 'page_title')
    list_filter = [ProcessSpellFilter]
    readonly_fields = (page_url, )
    form = SpelledPageAdminForm
    
    def mistakes(self, obj):
        return len(obj.results.splitlines())
    
    def page_title(self, obj):
        if not obj.title:
            return ''
        return obj.title
    
admin.site.register(SpelledPage, SpelledPageAdmin)

    
