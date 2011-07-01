# -*- coding: utf8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import time

from scrapy.utils.python import unicode_to_str

_MONTHS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"]

_INDEX_CLASSES = [
(u"Oro Spot Cierre Londres", "gold"), # this one must be in position 0
(u"Oro futuro cierre NY", "gold"),
(u"FED effective fund rate", "rate"),
(u"Tasa Libor 1 Mes", "rate"),
(u"Tasa Libor 1 Año", "rate"),
(u"Petroleo WTI Futuro", "commodity"),
(u"S&P500 Cierre NY", "stock"),
(u"Soja Futuro NY", "commodity"),
(u"Uruguay Bond Index", "spread"),
]

INDEX_NAMES = [x[0] for x in _INDEX_CLASSES]
INDEX_CLASSES = dict(_INDEX_CLASSES)

def get_index_class(name):
    if name in INDEX_CLASSES:
        return INDEX_CLASSES[name]
    elif "Tasa Objetivo" in name:
        return "rate"
    else:
        return "currency"

def get_index_order(name):
    if name in INDEX_NAMES:
        return INDEX_NAMES.index(name)
    elif "Tasa Objetivo" in name:
        return -1
    else:
        return 999

class IndexPrinter:
    
    def __init__(self):
        self.date = None
        self.indexes = []
        self.gold_price = None
        self.indexes_old = {} 
        self.gold_price_old = None
        self.show_year = False

    def set_date(self, date):
        self.date = date

    def append(self, item):
        self.indexes.append(item)
        if item["name"] == INDEX_NAMES[0]:
            self.gold_price = item["value"]
    
    def append_old(self, item):
        self.indexes_old[item["name"]] = item
        if item["name"] == INDEX_NAMES[0]:
            self.gold_price_old = item["value"]

    def __repr__(self):
        self.date = self.date or time.ctime()
        ret = u"%s\n" % self.date
        ret += u"-" * len(self.date) + "\n"
        ordered_indexes = sorted(self.indexes, key=lambda x: get_index_order(x["name"]))
        for index in ordered_indexes:
            ret += u"%(name)s: %(value)s%(unit)s" % index
            if get_index_class(index["name"]) in ["commodity", "stock"] and self.gold_price:
                ret += u"(%.5fozAu)" % (index["value"] / self.gold_price)
            old_index = self.indexes_old.get(index["name"])
            if old_index:
                ts = old_index["timestamp"]
                date = "%s %s" % (_MONTHS[ts.month-1], ts.day)
                if self.show_year:
                    date += " %s" % ts.year
                ret += u" [%s: %s%s" % (date, old_index["value"], old_index["unit"])
                if get_index_class(old_index["name"]) in ["commodity", "stock"] and self.gold_price_old:
                    ret += u" (%.5fozAu)" % (old_index["value"] / self.gold_price_old)
                ret += "]"
            ret += u"\n"
        return unicode_to_str(ret)
 
class GenericPrinter:
    def __init__(self, lformat, olformat=None):
        self.date = None
        self.items = []
        self.items_old = {}
        self.lformat = lformat
        self.olformat = olformat
        self.show_year = False

    def set_date(self, date):
        self.date = date
    def append(self, item):
        self.items.append(item)
    def append_old(self, item):
        self.items_old[item["name"]] = item
    def __repr__(self):
        self.date = self.date or time.ctime()
        ret = u"%s\n" % self.date
        ret += u"-" * len(self.date) + "\n"
        ordered_items = sorted(self.items, key=lambda x: x["name"])
        for item in ordered_items:
            ret += self.lformat % item
            if self.olformat:
                old_item = self.items_old.get(item["name"])
                if old_item:
                    ts = old_item["timestamp"]
                    date = "%s %s" % (_MONTHS[ts.month-1], ts.day)
                    if self.show_year:
                        date += " %s" % ts.year
                    ret += u" [%s: " % date + self.olformat % old_item + "]"
            ret += "\n"

        return unicode_to_str(ret)

