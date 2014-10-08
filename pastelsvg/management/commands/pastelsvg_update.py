import os, glob, re, time, datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from codefisher_apps.pastelsvg.models import Icon
from django.utils import timezone

class Command(BaseCommand):
    help = 'Updates the listing of icons in the database'

    def handle(self, *args, **options):
        files = glob.glob(os.path.join(settings.PASTEL_SVG_ICONS_FOLDER, "*.svg"))
        for filename in files:
            f = open(filename, 'rb')
            text = f.read()
            f.close()
            #print text
            match_title = re.search(r"<title>(.+)</title>", text).group(1)
            match_desc = re.search(r"<desc>(.+)</desc>", text).group(1)
            name = filename.rpartition('/')[2].partition('.')[0]
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
            modified = timezone.make_aware(modified, timezone.get_default_timezone())
            Icon.objects.update_or_create(file_name=name, 
                    defaults={"title": match_title, "description": match_desc, "date_modified": modified})