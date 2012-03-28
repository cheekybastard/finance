# -*- coding: utf8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import MySQLdb

from scrapy.xlib.pydispatch import dispatcher
from scrapy.signals import engine_stopped
from scrapy.exceptions import NotConfigured

from finance.items import FinanceIndex, Currency
from finance.utils.printers import IndexPrinter, GenericPrinter

class PrintIndexes(object):
    
    def __init__(self, settings):
        if not settings.get("ENABLE_PRINTED_REPORT"):
            raise NotConfigured

        dispatcher.connect(self.engine_stopped, engine_stopped)
        self.indexes = IndexPrinter()
        self.bonds = GenericPrinter("%(name)s (%(bondcoupon)s): %(bondprice)s/%(bondyield)s")
        self.currencies = GenericPrinter("%(name)s: %(value)s")
        self.gold_price = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):
        if isinstance(item, FinanceIndex):
            self.indexes.append(item)
        elif isinstance(item, Currency):
            self.currencies.append(item)
        else: # Bond
            self.bonds.append(item)
        return item
    
    def engine_stopped(self):
        print self.indexes
        print
        print self.bonds
        print
        print self.currencies
        print

class DBPipeline(object):
    def __init__(self, settings):
    
        if not settings.getbool("FINANCEDB_ENABLED"):
            raise NotConfigured

        db = MySQLdb.connect(user=settings.get("MYSQLDB_USER"), passwd=settings.get("MYSQLDB_PASS"),
                        db=settings.get("MYSQLDB_NAME"), use_unicode=True, charset='utf8')
        self.cursor = db.cursor()

    def process_item(self, item, spider):
        if isinstance(item, FinanceIndex):
            query = "INSERT INTO indices VALUES (null, '%s', '%s', %s, null)" % (item["name"],\
                     item["unit"], item["value"])
        elif isinstance(item, Currency):
            query = "INSERT INTO currencies VALUES (null, '%s', %s, null)" % (item["name"], item["value"])
        else: # Bond
            query = "INSERT INTO bonds VALUES (null, '%s', %s, %s, %s, null)" % (item["name"],
                     item["bondcoupon"], item["bondprice"], item["bondyield"])
        self.cursor.execute(query)
        spider.log("Stored: %s" % item["name"])
        return item

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
