import urllib2
import urlparse
import HTMLParser
import io
import operator

from PIL import Image
import Win32IconImagePlugin

class FavIconParser(HTMLParser.HTMLParser):

    def __init__(self, url):
        HTMLParser.HTMLParser.__init__(self)
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
        data = urllib2.urlopen(url).read()
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

def get_favicon_as_images(url):
    favicon_url = get_favicon_url(url)
    icon_fp = io.BytesIO(urllib2.urlopen(favicon_url, timeout=5).read())
    icons = file_to_images(icon_fp)
    icon_fp.close()
    return icons

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