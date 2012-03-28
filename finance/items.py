# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html
import re
from decimal import Decimal

from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import Compose

VALID_RE = re.compile("(1/)?([\d.,]+)")
VALPARTS_RE = re.compile("\d+")

def fixNumber(sval):
    """
    >>> fixNumber("0.25")
    '0.25'
    >>> fixNumber("6,25")
    '6.25'
    >>> fixNumber("1.166.59")
    '1166.59'
    >>> fixNumber("    3.76")
    '3.76'
    >>> fixNumber("4")
    '4'
    >>> fixNumber("1/5.0")
    '1/5.0'
    """

    r, val = VALID_RE.match(sval.strip()).groups()
    parts = VALPARTS_RE.findall(val)
    dpart = parts.pop(-1)
    if parts:
        return (r or "") + "".join(parts) + "." + dpart
    return (r or "") + dpart

takefirst = lambda x: x[0]

def todecimal(sval):
    r, val = VALID_RE.match(sval.strip()).groups()
    fval = float(val) if not r else 1/float(val)
    val = "%.4f" % fval
    return Decimal(val)

class FinanceIndex(Item):
    
    name = Field(output_processor=takefirst)
    value = Field(output_processor=Compose(takefirst, fixNumber, Decimal))
    unit = Field(output_processor=takefirst)

class Currency(Item):

    name = Field(output_processor=takefirst)
    value = Field(output_processor=Compose(takefirst, fixNumber, todecimal))

class Bond(Item):
   
    name = Field(output_processor=takefirst)
    bondyield =  Field(output_processor=Compose(takefirst, fixNumber, Decimal))
    bondprice = Field(output_processor=Compose(takefirst, fixNumber, Decimal))
    bondcoupon = Field(output_processor=Compose(takefirst, fixNumber, Decimal))

class Price(Item):

    name = Field(output_processor=takefirst)
    code = Field(output_processor=takefirst)
    value = Field(output_processor=Compose(takefirst, fixNumber, Decimal))


