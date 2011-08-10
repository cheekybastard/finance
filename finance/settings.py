# Scrapy settings for finance project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
# Or you can copy and paste them from where they're defined in Scrapy:
# 
#     scrapy/conf/default_settings.py
#
import os

BOT_NAME = 'finance'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['finance.spiders']
NEWSPIDER_MODULE = 'finance.spiders'
COMMANDS_MODULE = 'finance.commands'

DEFAULT_ITEM_CLASS = 'finance.items.FinanceIndex'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = ['finance.pipelines.PrintIndexes',
                  'finance.pipelines.DBPipeline']

SPIDER_SCHEDULER = "scrapy.contrib.spiderscheduler.FifoSpiderScheduler"

MYSQLDB_NAME = "finance"
MYSQLDB_USER = "finance"
# MYSQLDB_PASS =

# override in environment settings in order to store scraped values
FINANCEDB_ENABLED = False

try:
    from finance.local_settings import *
except:
    pass

