# -*- coding: utf8 -*-

from scrapy.spider import BaseSpider
from finance.items import FinanceIndex
from scrapy.contrib.loader import XPathItemLoader

class BCUSpider(BaseSpider):
    
    name = "bcu.gub.uy"

    start_urls = ["http://www.bcu.gub.uy/Politica-Economica-y-Mercados/Paginas/Tasas-Politica-Monetaria.aspx"]
    
    def parse(self, response):

        rate = XPathItemLoader(item=FinanceIndex(), response=response)
        
        rate.add_value("name", "Tasa Objetivo BCU")
        rate.add_value("unit", "%")
        rate.add_xpath("value", "8.75")
        #rate.update_only_if_change = True
        
        return [rate.load_item()]

CRAWLER = BCUSpider()
