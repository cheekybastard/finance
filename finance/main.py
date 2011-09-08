import os, datetime, logging, time

from twisted.internet import protocol, reactor
from twisted.internet.error import ProcessDone
from twisted.internet.threads import deferToThread

from scrapy import log
from scrapy.conf import settings

from finance import path

class Scraper():
    """Scraper process"""

    def __init__(self, crawler):
        self.procs = set()
        self.crawler = crawler
        self.spiders = self.crawler.spiders.list()

    def run(self):
        for i in range(settings.get("MAX_CRAWLERS")):
            self._create_crawler()

    def _create_crawler(self):
        if self.spiders:
            dfd = deferToThread(self._start_crawler, self.spiders.pop())
            dfd.addErrback(log.err)
            return dfd
        else:
            self.crawler.engine.stop()
    
    def _start_crawler(self, domain):
        """Run a scraping subprocess"""
        proc = ScrapyProcessProtocol(self, domain)
        progname = os.path.join(path, "bin", "finance-crawl")
        args = ["crawl", domain]
        reactor.spawnProcess(proc, progname, args=args, env=proc.env)
        self.procs.add(proc)
        return proc

    def processEnded(self, proc, status):
        log.msg("FinanceScraper: %s domain=%s pid=%d log=%s" % (proc.status, proc.domain, proc.pid, proc.logfile))
        if proc.errdata:
            log.msg(proc.errdata, logLevel=logging.DEBUG)
        self.procs.remove(proc)
        self._create_crawler()

    def connectionMade(self, proc):
        log.msg("FinanceScraper: started domain=%s pid=%s log=%s" % (proc.domain, proc.pid, proc.logfile))

class ScrapyProcessProtocol(protocol.ProcessProtocol):

    pid = -1
    start_time = None
    end_time = None

    def __init__(self, scraper, domain):
        self.status = "starting"
        self.scraper = scraper
        self.domain = domain
        logdir = os.path.join(settings.get("TEMPDIR"), domain)
        os.makedirs(logdir)
        self.logfile = os.path.join(logdir, time.strftime("%FT%T.log"))
        self.env = self._env()
        self.errdata = ""

    def errReceived(self, data):
        self.errdata += data

    def _env(self):
        env = os.environ.copy()
        env.update({
            'SCRAPY_LOG_FILE': self.logfile,
            'SCRAPY_WEBSERVICE_ENABLED': '0',
        })
        return env

    def connectionMade(self):
        self.status = "running"
        self.start_time = datetime.datetime.utcnow()
        self.pid = self.transport.pid
        self.transport.closeStdin()
        self.scraper.connectionMade(self)

    def processEnded(self, status):
        self.status = 'finished' if isinstance(status.value, ProcessDone) else 'terminated'
        self.end_time = datetime.datetime.utcnow()
        self.scraper.processEnded(self, status)


