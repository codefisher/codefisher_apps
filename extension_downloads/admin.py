import zipfile
import datetime
import xml.dom.minidom
from django.contrib import admin
from django import forms
from models import ExtensionDownload, Compatibility

class DownloadForm(forms.ModelForm):
    set_as_latest = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = ExtensionDownload
        fields = "__all__"

class DownloadAdmin(admin.ModelAdmin):
    fields = ("file", "release_notes", "group", "set_as_latest")
    list_display = ('title', 'version', 'release_date')
    form = DownloadForm

    def save_model(self, request, obj, form, change):
        if "file" in request.FILES:
            uploaded_file = request.FILES.get("file")
            obj.file_name = uploaded_file.name
            obj.file_size = uploaded_file.size
            obj.previous_release = obj.group.latest
            
            zip_file = zipfile.ZipFile(request.FILES.get("file"))
            try:
                install_rdf = zip_file.read("install.rdf")
            except:
                install_rdf = zip_file.read("about.xml")
            try:
                dom = xml.dom.minidom.parseString(install_rdf)
            except:
                dom = xml.dom.minidom.parseString(install_rdf.decode("iso-8859-1").encode("utf-8"))
            zip_file.close()
            try:
                obj.title = self._get_text(dom, "em:name")
            except:
                obj.title = self._get_text(dom, "name")
            try:
                obj.version = self._get_text(dom, "em:version")
            except:
                obj.version = self._get_text(dom, "version")
            try:
                obj.release_date = datetime.datetime(*zip_file.getinfo("install.rdf").date_time)
            except:
                obj.release_date = datetime.datetime(*zip_file.getinfo("about.xml").date_time)
            try:
                obj.description = self._get_text(dom, "em:description")
            except:
                obj.description = self._get_text(dom, "description")
            obj.save() # we know our parent class will do that
            for node in dom.getElementsByTagName("em:targetApplication"):
                app_id = self._get_text(node, "em:id")
                min = self._get_text(node, "em:minVersion")
                max = self._get_text(node, "em:maxVersion")
                comp = Compatibility(app_id=app_id, min_version=min, max_version=max, download=obj)
                comp.save()
        if form.cleaned_data.get("set_as_latest"):
            obj.group.latest = obj
            obj.group.save()
        super(DownloadAdmin, self).save_model(request, obj, form, change)

    def _get_text(self, dom, node_name):
        node = dom.getElementsByTagName(node_name)[0]
        rc = []
        for node in node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

admin.site.register(ExtensionDownload, DownloadAdmin)