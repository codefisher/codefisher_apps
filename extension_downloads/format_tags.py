from django.conf import settings
import djangopress.core.format.nodes as nodes
from codefisher_apps.extension_downloads.models import ExtensionDownload
from codefisher_apps.downloads.models import DownloadGroup

# this variable must be exposed, as it is searched for
library = nodes.Library

class ExtNode(nodes.TagNode):
    def __init__(self, token, ext_id):
        super(ExtNode, self).__init__(token)
        self.ext_id = ext_id

    def get_extension(self):
        try:
            group = DownloadGroup.objects.get(identifier=self.ext_id)
        except DownloadGroup.DoesNotExist:
            return None
        try:
            extension = ExtensionDownload.objects.get(pk=group.latest.pk)
        except ExtensionDownload.DoesNotExist:
            return None
        return extension

class ExtInfoNode(ExtNode):

    def render(self, context, **kwargs):
        extension = self.get_extension()
        if extension is None:
            return ""
        data = {
            "extension": extension,
            "compatibility": [(settings.MOZ_APP_NAMES.get(compat.app_id), compat.min_version, compat.max_version)
                              for compat in extension.compatibility.all() if compat.app_id in settings.MOZ_APP_NAMES],
        }
        return nodes.render("""
        <li>Name: <a href="{{ extension.group.homepage }}">{{ extension.title }}</a></li>
        <li>Released: {{ extension.release_date|date:"DATE_FORMAT" }}</li>
        <li>Version: <a href="{{ extension.get_absolute_url }}">{{ extension.version }}</a></li>
        <li>Compatibility:
            <ul>
                {% for app, min, max in compatibility %}
                    <li>{{ app }} {{ min }} to {{ max }}</li>
                {% endfor %}
            </ul>
        </li>
        <li>File size: {{ extension.file_size|filesizeformat }}</li>
        """, data)


def ext_info(parser, token):
    _, arg, kargs = nodes.tag_arguments(token.contents)
    return ExtInfoNode(token, arg if arg else kargs.get("id"))
nodes.Library.tag("ext_info", ext_info)

class ExtVersionNode(ExtNode):
    def render(self, context, **kwargs):
        extension = self.get_extension()
        if extension is None:
            return ""
        return extension.version

def ext_version(parser, token):
    _, arg, kargs = nodes.tag_arguments(token.contents)
    return ExtVersionNode(token, arg if arg else kargs.get("id"))
nodes.Library.tag("ext_version", ext_version)

class ExtLocationNode(ExtNode):
    def __init__(self, token, ext_id, download=False):
        super(ExtLocationNode, self).__init__(token, ext_id)
        self.download = download

    def render(self, context, **kwargs):
        extension = self.get_extension()
        if extension is None:
            return ""
        if self.download:
            return '''<a href="%s?download=true">''' % extension.get_absolute_url()
        return '''<a href="%s">''' % extension.get_absolute_url()

def ext_location(parser, token):
    _, arg, kargs = nodes.tag_arguments(token.contents)
    return ExtLocationNode(token, arg if arg else kargs.get("id"), kargs.get("download") == "true")
nodes.Library.tag("ext_location", ext_location)