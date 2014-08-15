from models import DownloadGroup, Download
from django.shortcuts import Http404, render_to_response, redirect
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponse

def release_notes(request, path, version,
        template_name="downloads/release_notes.html"):
    path_parts = path.split("/")
    folder = None
    for part in path_parts:
        try:
            folder = DownloadGroup.objects.get(slug=part, parent=folder,
                    sites__id__exact=settings.SITE_ID)
        except DownloadGroup.DoesNotExist:
            raise Http404
    if folder is None:
        raise Http404
    if version == "latest":
        download = folder.latest
    else:
        download = Download.objects.get(group=folder, version=version)
    data = {
        "download": download,
    }
    return render_to_response(template_name, data,
            context_instance=RequestContext(request))

def file_listing(request, path, template_name="downloads/index.html"):
    path_parts = path.split("/")
    if path_parts[-1] == '':
        folder = None
        for part in path_parts[:-1]:
            try:
                folder = DownloadGroup.objects.get(slug=part, parent=folder,
                        sites__id__exact=settings.SITE_ID)
            except DownloadGroup.DoesNotExist:
                raise Http404
        subfolders = DownloadGroup.objects.filter(parent=folder).order_by("title")
        downloads = Download.objects.filter(group=folder).order_by("-release_date")
        data = {
            "folder": folder,
            "subfolders": subfolders,
            "downloads": downloads,
        }
        return render_to_response(template_name, data,
                context_instance=RequestContext(request))
    else:
        folder = None
        for part in path_parts[:-1]:
            try:
                folder = DownloadGroup.objects.get(slug=part, parent=folder)
            except DownloadGroup.DoesNotExist:
                raise Http404
        if folder is None:
            raise Http404
        if path_parts[-1].split('.')[0] == "latest":
            download = folder.latest
        else:
            download = Download.objects.get(group=folder, file_name=path_parts[-1])
        url = "%s%s" % (settings.DOWNLOADS_FILE_LOCATION, download.file_name)
        if not settings.DOWNLOADS_FILE_PROXY:
            return redirect(url)
        else:
            responce = HttpResponse()
            responce["X-Accel-Redirect"] = url
            return responce