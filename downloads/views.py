from .models import DownloadGroup, Download
from django.shortcuts import Http404, render, redirect, get_object_or_404
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned

def release_notes(request, path, version,
        template_name="downloads/release_notes.html"):
    folder = DownloadGroup.objects.filter(version_path=path.strip('/'), sites__id__exact=settings.SITE_ID)
    if not folder.exists():
        raise Http404
    else:
        folder = folder[0]
    if version == "latest":
        download = folder.latest
    else:
        try:
            download = Download.objects.get(group__version_path=path.strip('/'), group__sites__id__exact=settings.SITE_ID, version=version)
        except MultipleObjectsReturned:
            # two objects with the same version, we just get the first, and hope
            # that is the right one.
            download = Download.objects.filter(group__version_path=path.strip('/'), group__sites__id__exact=settings.SITE_ID, version=version)[0]
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
    if not path or path[-1] == '/':
        folder = DownloadGroup.objects.filter(path=path.strip('/'), sites__id__exact=settings.SITE_ID)
        if folder.exists():
            folder = folder[0]
            subfolders = DownloadGroup.objects.filter(parent__path=path.strip('/'), sites__id__exact=settings.SITE_ID).order_by("title")
            downloads = Download.objects.filter(group__path=path.strip('/'), group__sites__id__exact=settings.SITE_ID).order_by("-release_date")
        else:
            subfolders = DownloadGroup.objects.filter(parent=None, sites__id__exact=settings.SITE_ID).order_by("title")
            downloads = None          
        data = {
            "folder": folder,
            "title": folder.title if folder else "Downloads",
            "subfolders": subfolders,
            "downloads": downloads,
        }
        return render(request, template_name, data)
    else:
        # is possible to configure nginx etc, so this never runs, but for 
        # testing this is good
        path_parts = path.split('/')
        folder_path = '/'.join(path_parts[:-1])
        folder = DownloadGroup.objects.filter(path=folder_path.strip('/'), sites__id__exact=settings.SITE_ID)
        if not folder.exists():
            raise Http404
        else:
            folder = folder[0]
        if path_parts[-1].split('.')[0] == "latest":
            return redirect(folder.latest.get_absolute_url())
        else:
            download = get_object_or_404(Download, group__path=folder_path.strip('/'), group__sites__id__exact=settings.SITE_ID, file_name=path_parts[-1])
            return redirect(download.file.url)
