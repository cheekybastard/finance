from scrapy.command import ScrapyCommand

import MySQLdb

from scrapy.conf import settings

from finance.utils.printers import IndexPrinter, GenericPrinter

class Command(ScrapyCommand):
    
    def syntax(self):
        return "[options]"

    def short_desc(self):
        return "Print finance report"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("-d", "--date", help="Print data for given date (in format yyyy-mm-dd, by default is last stored data)")
        parser.add_option("-c", "--compare", metavar="DATE", help="Compare with data on given date (in format yyyy-mm-dd)")
        parser.add_option("-D", "--day", action="store_true", help="Compare with previous day")
        parser.add_option("-W", "--week", action="store_true", help="Compare with previous week")
        parser.add_option("-M", "--month", action="store_true", help="Compare with previous month")
        parser.add_option("-4", "--four_month", action="store_true", help="Compare with previous 4 month")
        parser.add_option("-Y", "--year", action="store_true", help="Compare with previous year")
        parser.add_option("--show_year", action="store_true", help="Show year of comparing date in report")

    def run(self, args, opts):

        db = MySQLdb.connect(user=settings.get("MYSQLDB_USER"), passwd=settings.get("MYSQLDB_PASS"),
                      db=settings.get("MYSQLDB_NAME"), use_unicode=True, charset='utf8')

        cursor = db.cursor()

        date = "'%s'" % opts.date if opts.date else "CURDATE()"
        old_date = None
        if opts.compare:
            old_date = "'%s'" % opts.compare
        elif opts.day:
            old_date = "SUBDATE(%s, '1')" % date
        elif opts.week:
            old_date = "SUBDATE(%s, '7')" % date
        elif opts.month:
            old_date = "SUBDATE(%s, '30')" % date
        elif opts.four_month:
            old_date = "SUBDATE(%s, '120')" % date
        elif opts.year:
            old_date = "SUBDATE(%s, '365')" % date

        # indices
        for table in ["indices", "bonds", "currencies"]:
            cursor.execute("SELECT DISTINCT name FROM %s" % table)
            item_names = [r[0] for r in cursor.fetchall()]
            if table == "indices":
                items = IndexPrinter()
            elif table == "bonds":
                items = GenericPrinter("%(name)s (%(coupon)s): %(price)s/%(yield)s", "%(price)s/%(yield)s")
            else: # currencies
                items = GenericPrinter("%(name)s: %(value)s", "%(value)s")
            items.show_year = opts.show_year

            cursor.execute("DESCRIBE %s" % table)
            item_keys = tuple([r[0] for r in cursor.fetchall()])

            for name in item_names:
                cursor.execute("SELECT * FROM %s WHERE name='%s' AND DATE(timestamp) <= %s ORDER BY timestamp DESC LIMIT 1" % (table, name, date))
                data = cursor.fetchone()
                if data:
                    items.append(dict(zip(item_keys, data)))
                    items.set_date(data[-1].ctime())

            if old_date:
                for name in item_names:
                    cursor.execute("SELECT * FROM %s WHERE name='%s' AND DATE(timestamp) <= %s ORDER BY timestamp DESC LIMIT 1" % (table, name, old_date))
                    data = cursor.fetchone()
                    if data:
                        items.append_old(dict(zip(item_keys, data)))

            print items

