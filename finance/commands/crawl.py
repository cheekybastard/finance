from scrapy.commands.crawl import Command as CrawlCommand
from scrapy.conf import settings

class Command(CrawlCommand):
    
    def syntax(self):
        return "[spider list]"

    def short_desc(self):
        return "Crawl spiders"

    def add_options(self, parser):
        CrawlCommand.add_options(self, parser)
        parser.add_option("--db", action="store_true", help="Save scraped data into application db")

    def process_options(self, args, opts):
        CrawlCommand.process_options(self, args, opts)
        if opts.db:
            settings.overrides['FINANCEDB_ENABLED'] = True

    def run(self, args, opts):
        CrawlCommand.run(self, args, opts)
