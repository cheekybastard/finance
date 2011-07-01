# -*- coding: utf8 -*-

from scrapy.spider import BaseSpider
from scrapy.contrib.loader import XPathItemLoader

from finance.items import FinanceIndex

class KitcoSpider(BaseSpider):
    
    name = "kitco.com"

    start_urls = ["http://www.kitco.com/gold.londonfix.html"]
    
    def parse(self, response):
        
        gold = XPathItemLoader(item=FinanceIndex(), response=response)
        gold.add_value("name", "Oro Spot Cierre Londres")
        gold.add_value("unit", "USD")
        gold.add_xpath("value", "//td[@bgcolor='#cccc99'][1]//text()")

        return [gold.load_item()]

CRAWLER = KitcoSpider()
