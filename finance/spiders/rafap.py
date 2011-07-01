# -*- coding: utf8 -*-

from scrapy.spider import BaseSpider
from scrapy.contrib.loader import XPathItemLoader

from finance.items import FinanceIndex

class RafapSpider(BaseSpider):
    
    name = "rafap.com.uy"

    start_urls = ["http://www4.rafap.com.uy/internet/servlet/hvisins?1"]
    
    def parse(self, response):
        
        ubi = XPathItemLoader(item=FinanceIndex(), response=response)
        ubi.add_value("name", "Uruguay Bond Index")
        ubi.add_value("unit", "bps")
        ubi.add_xpath("value", "//span/text()")

        return [ubi.load_item()]

CRAWLER = RafapSpider()
