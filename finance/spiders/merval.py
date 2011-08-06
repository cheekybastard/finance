# -*- coding: utf8 -*-

from scrapy.spider import BaseSpider

from finance.items import FinanceIndex
from scrapy.contrib.loader import XPathItemLoader
from scrapy.selector import HtmlXPathSelector

class MervalSpider(BaseSpider):
    
    name = "merval.sba.com.ar"

    start_urls = ["http://www.merval.sba.com.ar/"]
    
    def parse(self, response):

        rate = XPathItemLoader(item=FinanceIndex(), response=response)
        
        rate.add_value("name", "Merval")
        rate.add_value("unit", "")

        hxs = HtmlXPathSelector(response)
        rate.add_value("value", hxs.select("//span[contains(@id,'UltimoMerval')]/text()")[0].extract())
        
        return [rate.load_item()]

CRAWLER = MervalSpider()
