from scrapy.commands.crawl import Command as CrawlCommand
from scrapy.conf import settings

class Command(CrawlCommand):
    
    def syntax(self):
        return "[spider list]"

    def short_desc(self):
        return "Crawl and store data in db"

    def run(self, args, opts):
        settings.overrides['FINANCEDB_ENABLED'] = True
        CrawlCommand.run(self, args, opts)

