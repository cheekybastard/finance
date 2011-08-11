import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from finance.items import FinanceIndex, Bond, Currency
from scrapy.contrib.loader import XPathItemLoader

from scrapy.http import Request

_COMMODITIES =  [
    ("GOLD", "Oro futuro cierre NY"),
    ("SILVER", "Plata futuro cierre NY"),
    ("WTI CRUDE", "Petroleo WTI Futuro"),
    ("SOYBEAN FUTURE", "Soja Futuro NY"),
    ("LIVE CATTLE", "Ganado en Pie Futuro"),
    ("WHEAT FUTURE(CBT)", "Trigo futuro (CBT)"),
]

class BloombergSpider(BaseSpider):
    name = "bloomberg.com"
    start_urls = [
    "http://www.bloomberg.com/markets/commodities/futures/",
    "http://www.bloomberg.com/markets/stocks/",
    "http://www.bloomberg.com/markets/rates-bonds/government-bonds/brazil/",
    "http://www.bloomberg.com/markets/rates-bonds/government-bonds/germany/",
    "http://www.bloomberg.com/markets/rates-bonds/government-bonds/us/",
    "http://www.bloomberg.com/markets/currencies/",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        def get_index_values(text):
            name = hxs.select("//td[@class='name'][contains(text(), '%s')]/text()" % text).extract()
            values = hxs.select("//td[@class='name'][contains(text(), '%s')]/following-sibling::td/text()" % text).extract()
            unit = hxs.select("//td[@class='name'][contains(text(), '%s')]" % text).re("\((US.*)\)")
            unit = unit[0] if unit else ""
            return name, values, unit

        def get_bond(name, bondname=None):
            bond = XPathItemLoader(item=Bond(), response=response)
            name, values, _ = get_index_values(name)
            bond.add_value("name", bondname or name)
            bond.add_value("bondcoupon", values[0])
            price, byield = values[2].split('/')
            bond.add_value("bondprice", price)
            bond.add_value("bondyield", byield)
            return bond

        items = []
        if "commodities" in response.url:
            for i in _COMMODITIES:
                index = XPathItemLoader(item=FinanceIndex(), response=response)
                index.add_value("name", i[1])
                _, values, unit = get_index_values(i[0])
                index.add_value("value", values[0])
                index.add_value("unit", unit)
                items.append(index.load_item())

        elif "stocks" in response.url:
            index = XPathItemLoader(item=FinanceIndex(), response=response)
            index.add_value("name", "S&P500 Cierre NY")
            _, values, unit = get_index_values("S&P 500")
            index.add_value("value", values[0])
            index.add_value("unit", unit)
            items.append(index.load_item())

        elif "/brazil/" in response.url:
            for name in ["Brazil", "Mexico", "Colombia", "Panama", "Chile", "Peru", "Venezuela"]:
                items.append(get_bond(name).load_item())

        elif "/germany/" in response.url:
            items.append(get_bond("10-Year", "Germany 10-Year").load_item())

        elif "/us/" in response.url:
            items.append(get_bond("10-Year", "USA 10-Year").load_item())
        elif "/currencies/" in response.url:
            lines = hxs.select("//script[contains(text(), 'var price = new Object();')]").extract()[0].splitlines()
            xrates = dict([
                ('ARS','Peso argentino'),
                ('AUD', 'Australian Dollar'),
                ('BRL','Real'),
                ('EUR', 'Euro'),
                ('GBP', 'Libra'),
                ('UYU', 'Peso uruguayo'),
                ('CNY', 'Renminbi'),
                ('JPY', 'Yen'),
                ('SEK', 'Krona'),
                ('SGD', 'Singapore Dollar'),
                ('CHF', 'Swiss Franc'),
            ])
            cur_re = re.compile("([A-Z][A-Z][A-Z]):CUR'\] = (\d+\.\d+)")
            for line in lines:
                m = cur_re.search(line)
                if m and m.groups()[0] in xrates:
                    key, val = m.groups()
                    name = xrates[key]
                    cur = XPathItemLoader(item=Currency(), response=response)
                    
                    if key in ['AUD', 'GBP', 'EUR']:
                        cur.add_value("name", "%s (%s/USD)" % (name, key))
                        cur.add_value("value", "1/%s" % val)
                    else:
                        cur.add_value("name", "%s (USD/%s)" % (name, key))
                        cur.add_value("value", val)

                    items.append(cur.load_item())

        return items
        
SPIDER = BloombergSpider()
