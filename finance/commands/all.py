from finance.commands.crawl import Command as CrawlCommand
from finance.main import Scraper

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

class Command(CrawlCommand):
    def syntax(self):
        return ""

    def short_desc(self):
        return "Run all spiders"

    def run(self, args, opts):
        self.scraper = Scraper(self.crawler)
        
        dispatcher.connect(self.engine_started, signal=signals.engine_started)

        self.crawler.start()

    def engine_started(self):
        self.scraper.run()
