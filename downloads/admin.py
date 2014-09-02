from django.contrib import admin
from django import forms
from models import DownloadGroup, Download

class DownloadForm(forms.ModelForm):
    set_as_latest = forms.BooleanField(required=False)

    class Meta:
        model = Download
        fields = "__all__"

class DownloadAdmin(admin.ModelAdmin):
    form = DownloadForm

    fields = ("group", "title", "file", "version", "homepage", "release_date", "description", "release_notes", "previous_release", "set_as_latest")
    list_display = ('title', 'version', 'release_date')

    def save_model(self, request, obj, form, change):
        if "file" in request.FILES:
            uploaded_file = request.FILES.get("file")
            obj.file_name = uploaded_file.name
            obj.file_size = uploaded_file.size
            obj.previous_release = obj.group.latest
            obj.save()
        if form.cleaned_data.get("set_as_latest"):
            obj.group.latest = obj
            obj.group.save()
        super(DownloadAdmin, self).save_model(request, obj, form, change)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'version_slug', 'parent')

admin.site.register(DownloadGroup, GroupAdmin)
admin.site.register(Download, DownloadAdmin)