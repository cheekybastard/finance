# -*- coding: utf8 -*-
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader

from finance.items import FinanceIndex

class BankrateSpider(BaseSpider):
    
    name = "bankrate.com"

    start_urls = ['http://www.bankrate.com/rates/interest-rates/libor.aspx']
    
    def parse(self, response):
        
        hxs = HtmlXPathSelector(response)
        def get_rate(text):
            return hxs.select("//td[@class='tabledataoddnew']//strong[contains(text(), '%s')]/../../following-sibling::td/text()" % text )[0].extract()
        
        monthrate = XPathItemLoader(item=FinanceIndex(), response=response)
        annualrate = XPathItemLoader(item=FinanceIndex(), response=response)
        
        monthrate.add_value("name", "Tasa Libor 1 Mes")
        monthrate.add_value("unit", "%")
        monthrate.add_value("value", get_rate("1 Month LIBOR Rate"))
        
        annualrate.add_value("name", u"Tasa Libor 1 Año")
        annualrate.add_value("unit", "%")
        annualrate.add_value("value", get_rate("1 Year LIBOR Rate"))
        
        return [monthrate.load_item(), annualrate.load_item()]

CRAWLER = BankrateSpider()
