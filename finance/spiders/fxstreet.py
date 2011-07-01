# -*- coding: utf8 -*-

from scrapy.spider import BaseSpider
from scrapy.contrib.loader import XPathItemLoader

from finance.items import FinanceIndex

rates = [
("Tasa Objetivo European CB", "European Monetary", 1),
("Tasa Objetivo Sveriges Riksbank", "Sweden", 1),
('Tasa Objetivo Bank of Japan', "Japan", 1),
('Tasa Objetivo CB of China','China', 1),
('Tasa Objetivo BC do Brasil','Brazil', 1),
('Tasa Objetivo Bank of England', 'United Kingdom', 1),
('Tasa Objetivo Reserve Bank of Australia', 'Australia', 1),
]

class FxStreetSpider(BaseSpider):
    
    name = "fxstreet.com"

    start_urls = ["http://www.fxstreet.com/fundamental/interest-rates-table/"]
    
    def parse(self, response):
        
        items = []
        for name, pattern, pos in rates:
            rate = XPathItemLoader(item=FinanceIndex(), response=response)
            rate.add_value("name", name)
            rate.add_value("unit", "%")
            rate.add_xpath("value", "//a[contains(text(), '%s')]/parent::td/following-sibling::td[%d]/text()" % (pattern, pos))
            items.append(rate.load_item())
        return items

CRAWLER = FxStreetSpider()
