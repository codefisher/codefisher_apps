from django.core.management.base import BaseCommand
from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy import log, signals
from django.utils.encoding import force_unicode
from django.conf import settings

import re
from urlparse import urlparse
from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector
from collections import defaultdict
from djangopress.core.format.stripped_html import stripped_html
from codefisher_apps.site_crawler.models import CrawlProcess, CrawledPage, SpelledPage
from scrapy.contrib.djangoitem import DjangoItem

from enchant import DictWithPWL
from enchant.checker import SpellChecker
from enchant.tokenize import HTMLChunker, EmailFilter, URLFilter
django.utils.encoding import DjangoUnicodeDecodeError

class Page(DjangoItem):
    django_model = CrawledPage
    
class SpellingPage(DjangoItem):
    django_model = SpelledPage
    
class BaseSiteSpider(CrawlSpider):
    
    def __init__(self, **kw):
        super(BaseSiteSpider, self).__init__(**kw)
        url = kw.get('url') or kw.get('domain')
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://%s/' % url
        self.url = url
        self.process = kw.get('process')
        self.deny = [re.compile(x) for x in kw.get('deny', [])]
        self.allowed_domains = [urlparse(url).hostname.lstrip('www.')]
        self.link_extractor = SgmlLinkExtractor()
        #self.cookies_seen = set()
        
    def clean_up(self):
        pass
        
    def setup(self):
        pass
    
    def start_requests(self):
        return [Request(self.url, callback=self.parse)]
    
    def parse(self, response):
        page = self._get_item(response)
        r = [page]
        r.extend(self._extract_requests(response))
        return r
    
    def _should_follow(self, url):
        for pattern in self.deny:
            if pattern.search(url) is not None:
                return False
        return True
    
    def _set_title(self, page, response):
        if isinstance(response, HtmlResponse):
            title = Selector(response).xpath("//title/text()").extract()
            if title:
                page['title'] = title[0]

    def _set_new_cookies(self, page, response):
        cookies = []
        for cookie in [x.split(';', 1)[0] for x in response.headers.getlist('Set-Cookie')]:
            if cookie not in self.cookies_seen:
                self.cookies_seen.add(cookie)
                cookies.append(cookie)
        if cookies:
            page['newcookies'] = cookies
            
    def _extract_requests(self, response):
        r = []
        if isinstance(response, HtmlResponse):
            links = (x for x in self.link_extractor.extract_links(response) if self._should_follow(x.url))
            r.extend(Request(x.url, callback=self.parse) for x in links)
        return r
        
class SiteCheckerSpider(BaseSiteSpider):

    name = 'site_crawler'
    handle_httpstatus_list = [404, 500, 301, 302, 307, 401, 403]

    def __init__(self, **kw):
        super(SiteCheckerSpider, self).__init__(**kw)
        self.link_map = defaultdict(list)
        self.link_extractor = SgmlLinkExtractor(tags=('a', 'area', 'img', 'link', 'script'), attrs=('href', 'src'), deny_extensions=())

    def set_up(self):
        CrawledPage.objects.filter(process=self.process).delete()
        
    def clean_up(self):
        for url, links in self.link_map.items():
            CrawledPage.objects.filter(url=url).update(parents="\n".join(links))
    
    def parse(self, response):
        page = self._get_item(response)
        r = [page]
        if response.status in (301, 302, 307):
            r.append(Request(response.headers.get('Location'), callback=self.parse, meta={'dont_redirect': True}))
        else:
            r.extend(self._extract_requests(response))
        return r

    def _get_item(self, response):
        page = Page(url=response.url, size=len(response.body), status=response.status, process=self.process)
        if response.status == 200:
            self._set_title(page, response)
            #self._set_new_cookies(page, response)
        page.save()
        return page

    def _extract_requests(self, response):
        r = []
        if isinstance(response, HtmlResponse):
            links = [x for x in self.link_extractor.extract_links(response) if self._should_follow(x.url)]
            for x in links:
                self.link_map[x.url].append(response.url)
            r.extend(Request(x.url, callback=self.parse, meta={'dont_redirect': True}) for x in links)
        return r

class SiteSpellerSpider(BaseSiteSpider):

    name = 'site_speller'
    
    def setup(self):
        SpelledPage.objects.filter(process=self.process).delete()
        
    def _get_item(self, response):
        try:
            word_dict = DictWithPWL(settings.SITE_CRAWLER_DICT_LANG, settings.SITE_CRAWLER_DICT_PWL)
            spell_checker = SpellChecker(word_dict, re.sub(r'\s+', ' ', stripped_html(force_unicode(response.body))), filters=(EmailFilter, URLFilter))
            results = "\n".join(set(x.word for x in spell_checker))
        except DjangoUnicodeDecodeError:
            results = "" # might happen with binary file, or something really messed up
        page = SpellingPage(url=response.url, results=results, size=len(response.body), process=self.process)
        self._set_title(page, response)
        #self._set_new_cookies(page, response)
        page.save()
        return page

CRAWLERS = {
           SiteCheckerSpider.name: SiteCheckerSpider,
           SiteSpellerSpider.name: SiteSpellerSpider
}

class Command(BaseCommand):
    help = 'Crawls the site and performs a number of operations on the data'

    def handle(self, *args, **options):
        if len(args) == 0:
            return "Must give a name of the crawler to use."
        try:
            process = CrawlProcess.objects.get(name=args[0])
        except CrawlProcess.DoesNotExist:
            return "The named crawl process does not exist"
        crawler_class = CRAWLERS.get(process.crawler)
        if not crawler_class:
            return "The crawler does not exist."
        
        spider = crawler_class(process=process, domain=process.domain, deny=process.deny.splitlines())
        spider.setup()
        crawler = Crawler(Settings({'DOWNLOAD_DELAY': 0}))
        crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        crawler.configure()
        crawler.crawl(spider)
        crawler.start()
        log.start()
        reactor.run()
        spider.clean_up()