from django.db import models
from django import forms
import xml.dom.minidom
import urllib2
from django.template.loader import render_to_string
from djangopress.pages.blocks import PageBlock
from django.conf import settings


class FeedBlock(PageBlock):
    name = "Feed"

    FEED_TYPES = (
        ("rss", "RSS"),
    )

    template_name = models.CharField(max_length=50, choices=settings.FEED_BLOCK_TEMPLATES)
    feed_url = models.CharField(max_length=255)
    feed_type = models.CharField(max_length=4, choices=FEED_TYPES)

    def get_text(self, node):
        rc = []
        for node in node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)


    def content(self, context):
        fp = urllib2.urlopen(self.feed_url)
        dom = xml.dom.minidom.parse(fp)
        fp.close()

        item_nodes = dom.getElementsByTagName("item")
        items = []
        for node in item_nodes:
            item = {
                "link": self.get_text(node.getElementsByTagName("link")[0]),
                "title": self.get_text(node.getElementsByTagName("title")[0]),
            }
            items.append(item)

        data = {
            "title": self.get_text(dom.getElementsByTagName("title")[0]),
            "items": items,
        }
        return render_to_string(self.template_name, data, context_instance=context)

class FeedForm(forms.ModelForm):
    template = None

    class Meta:
        model = FeedBlock
        widgets = {
            'block_name': forms.HiddenInput()
        }
FeedBlock.form = FeedForm