from models import DownloadGroup, Download
from django.shortcuts import Http404, render, redirect, get_object_or_404
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned

def release_notes(request, path, version,
        template_name="downloads/release_notes.html"):
    path_parts = path.split("/")
    folder = None
    for part in path_parts:
        folder = get_object_or_404(DownloadGroup, version_slug=part, parent=folder,
                    sites__id__exact=settings.SITE_ID)
    if version == "latest":
        download = folder.latest
    else:
        try:
            download = Download.objects.get(group=folder, version=version)
        except MultipleObjectsReturned:
            # two objects with the same version, we just get the first, and hope
            # that is the right one.
            download = Download.objects.filter(group=folder, version=version)[0]
        except:
            return render(request, "downloads/not_found.html", {"folder": folder})
    if not download.release_notes:
        raise Http404
    data = {
        "title": "%s %s" % (download.title, download.version),
        "download": download,
    }
    return render(request, template_name, data)

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
            "title": folder.title,
            "subfolders": subfolders,
            "downloads": downloads,
        }
        return render(request, template_name, data)
    else:
        # is possible to configure nginx etc, so this never runs, but for 
        # testing this is good
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
            download = get_object_or_404(Download, group=folder, file_name=path_parts[-1])
        return redirect(download.file.url)
