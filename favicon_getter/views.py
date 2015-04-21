try:
    from urllib2 import urlopen
    import urlparse
    from HTMLParser import HTMLParser
except ImportError:
    from urllib.request import urlopen
    import urllib.parse as urlparse
    from html.parser import HTMLParser
import io
import operator
import subprocess
import base64

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django import forms
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.http import HttpResponse

from PIL import Image

class FavIconParser(HTMLParser):

    def __init__(self, url):
        HTMLParser.__init__(self)
        self._icons = []
        self._url = url

    def handle_starttag(self, tag, attrs):
        if tag == "link":
            attrs = dict(attrs)
            if attrs["rel"].find("icon") != -1 and "href" in attrs:
                self._icons.append(urlparse.urljoin(self._url, attrs["href"]))

    def get_icon(self):
        if not self._icons:
            return None
        return self._icons.pop(0)

def get_favicon_url(url):
    try:
        data = urlopen(url).read()
    except IOError:
        return None
    try:
        parser = FavIconParser(url)
        parser.feed(data)
        parser.close()
    except HTMLParser.HTMLParseError:
        return None
    icon_url = parser.get_icon()
    if not icon_url:
        icon_url = urlparse.urljoin(url, "/favicon.ico")
    return icon_url

def file_to_images(fp):
    try:
        image = Image.open(fp)
        if "sizes" in image.info:
            images = []
            for size in image.info["sizes"]:
                image.size = size
                im = Image.new("RGBA", size)
                im.putdata(image.getdata())
                images.append((im, im.size))
            return images
        return [(image, image.size)]
    except:
        return None

def get_favicon_as_images(url=None, favicon_url=None):
    try:
        if not favicon_url:
            favicon_url = get_favicon_url(url)
        fav = urlopen(favicon_url, timeout=10)
        icon_fp = io.BytesIO(fav.read())
        fav.close()
        icons = file_to_images(icon_fp)
        #icon_fp.close() # we get errors latter if we close this now
        return icons
    except:
        return None
    
@csrf_exempt
def favicons(request):
    if not request.POST.get("url"):
        return HttpResponse("fail")
    url = request.POST.get("url")
    parsed_url = urlparse.urlparse(url)
    if parsed_url[0] == "":
        url = "http://" + url
    elif parsed_url[0] not in ["http", "https", "ftp", "ftps"]:
        return HttpResponse("fail")
    icons = get_favicon_as_images(url)  
    if icons is None:
        return HttpResponse("fail")
    icons = get_favicon_as_images(url)  
    tags = get_tags(icons)
    return HttpResponse("\n".join(tags))

def get_sized_icons(url, sizes):
    icons = get_favicon_as_images(url)
    if icons is None:
        return None
    largest, _ = max(icons, key=operator.itemgetter(1))
    result = {}
    for image, size in icons:
        width, height = size[0:2]
        if width == height and height in sizes:
            result[width] = image
    for size in set(sizes).difference(set(result.keys())):
        result[size] = largest.resize((size, size))
    return result

@csrf_exempt # we do this, or we can't change the upload_handlers
def index(request):
    request.upload_handlers.insert(0, TemporaryFileUploadHandler())
    tags = []
    ico = True
    if request.method == "POST":
        if "ico-to-png" in request.POST:
            if "ico-file" in request.FILES:
                icons = file_to_images(request.FILES["ico-file"].file)
                if icons:
                    tags = get_tags(icons)
        elif "png-to-ico" in request.POST:
            name = "png-file-1"
            index = 1
            files = []
            while name in request.FILES:
                files.append(request.FILES[name].temporary_file_path())
                index += 1
                name = "png-file-%s" % index
            try:
                ico_data = subprocess.check_output(["icotool", "-c"] + files)
                responce = HttpResponse(ico_data, content_type="application/octet-stream")
                responce['Content-Disposition'] = 'attachment; filename=icon.ico'
                return responce
            except subprocess.CalledProcessError:
                ico = False
    data = {
        "title": "ICO tools",
          "pngs": "\n".join(tags),
          "ico": ico,
    }
    return render(request, "ico/index.html", data)

class  UrlForm(forms.Form):
    url = forms.URLField(label="Website Url")
    
def get_tags(icons):
    tags = []
    for icon, size in icons:
        value = io.BytesIO()
        icon.save(value, "png")
        data = "data:image/png;base64," + base64.b64encode(value.getvalue())
        value.close()
        tags.append('<img style="margin:10px;" src="%s" width="%s" height="%s" alt="">' % (data, size, size))
    return tags
    
def favicon(request):
    tags = []
    submitted = False
    favicon_url = None
    if request.method == "POST":
        form = UrlForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            favicon_url = get_favicon_url(url)
            icons = get_favicon_as_images(favicon_url=favicon_url)
            if icons:
                tags = get_tags(icons)
                submitted = True
    else:
        form = UrlForm()
    data = {
            "title": "Get Favicon",
            "form": form,
            "tags": "".join(tags),
            "submitted": submitted,
            "favicon_url": favicon_url,
    }
    return render(request, "ico/favicon.html", data)