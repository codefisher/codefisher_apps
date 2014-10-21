from django.contrib import admin
from codefisher_apps.pastelsvg.models import Icon, PastelSVGDonation, ProtectedDownload, IconRequest, IconRequestComment, UseExample
from django.conf import settings
from upvotes.admin import RequestAdmin, RequestCommentAdmin

admin.site.register(IconRequest, RequestAdmin) 
admin.site.register(IconRequestComment, RequestCommentAdmin)

class IconAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'icon', 'title', 'description', 'date_modified')
    
    def icon(self, obj):
        return '<img alt="%s" src="%s16/%s.png">' % (obj.file_name, settings.PASTEL_SVG_WEB, obj.file_name)
    icon.allow_tags = True
    
admin.site.register(Icon, IconAdmin)


class PastelSVGDonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amount', 'validated')
    
admin.site.register(PastelSVGDonation, PastelSVGDonationAdmin)

class UseExampleAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'author_name', 'posted', 'validated')
    
admin.site.register(UseExample, UseExampleAdmin)

class ProtectedDownloadAdmin(admin.ModelAdmin):
    list_display = ('title', 'version', 'file', 'release_date')
    fields = ('file', 'title', 'version', 'description', 'public')
    
    def save_model(self, request, obj, form, change):
        if "file" in request.FILES:
            uploaded_file = request.FILES.get("file")
            obj.file_name = uploaded_file.name
            obj.file_size = uploaded_file.size
            obj.save()
        super(ProtectedDownloadAdmin, self).save_model(request, obj, form, change)
        
admin.site.register(ProtectedDownload, ProtectedDownloadAdmin)