# -*- coding: utf8 -*-
import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from finance.items import FinanceIndex
from scrapy.contrib.loader import XPathItemLoader

class FederalReserveSpider(BaseSpider):
    
    name = "federalreserve.gov"

    start_urls = ["http://www.federalreserve.gov/monetarypolicy/openmarket.htm",
                  "http://www.federalreserve.gov/releases/h15/update/"]
    
    def parse(self, response):
        
        hxs = HtmlXPathSelector(response)
        
        if "openmarket" in response.url:
            rate = XPathItemLoader(item=FinanceIndex(), response=response)
            rate.add_value("name", "Tasa Objetivo FED")
            rate.add_value("unit", "%")
            rate.add_value("value", hxs.select("//td[@class='data'][3]/text()").re("\d+\.\d+"))
            #rate.update_only_if_change = True

            return [rate.load_item()]
        else:
            for line in response.body_as_unicode().splitlines():
                if "Federal funds (effective)" in line:
                    rate = XPathItemLoader(item=FinanceIndex(), response=response)
                    rate.add_value("name", "FED effective fund rate")
                    rate.add_value("unit", "%")
                    rate.add_value("value", hxs.select("//th[contains(text(), 'Federal funds')]/following-sibling::td/text()").re("\xa0(.*?)\xa0"))
                    return [rate.load_item()]

CRAWLER = FederalReserveSpider()
