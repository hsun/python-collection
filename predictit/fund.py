#!/usr/bin/env python

import sys, operator
from siteutil import Site
from BeautifulSoup import BeautifulSoup
from statlib import stats
from debug import say
from optutil import get_opts
from msn import MsnReport
import yahoo

if __name__ == '__main__':

    opts = get_opts({"s" : "symbol"})
    symbol = opts["symbol"].upper()

    data = yahoo.get_all(symbol)
    print "Symbol -- %s (%s)" % (symbol, data['market_cap'])

    print "---- Market ----"
    print "Quote: %s Change: %s" % (data['price'], data['change'])
    print "52-w High: %.2f 52-w Low: %.2f" % (float(data['52_week_high']), float(data['52_week_low']))
    print "50 SMA: %.2f 200 SMA: %.2f" % (float(data['50day_moving_avg']), float(data['200day_moving_avg']))
    volume = float(data['volume'])
    avg_volume = float(data['avg_daily_volume'])
    print "Volumn: %.0f Change: %.2f%%" % (volume, (volume - avg_volume)/volume * 100.0)
    print "Book Value: %s Price Book Ration: %s" % (data['book_value'], data['price_book_ratio'])
    print "EPS: %s Price Earning Ration: %s Price Earning Growth Ration: %s" % \
        (data['earnings_per_share'], data['price_earnings_ratio'], data['price_earnings_growth_ratio'])
    print "Ebitda: %s Price Sales raio: %s" % (data['ebitda'], data['price_sales_ratio'])
    print "Dividend Yield: %s Divident Per Share: %s" % (data['dividend_yield'], data['dividend_per_share'])
    print "Short Ratio: %s" % (data['short_ratio'])

    msn_report = MsnReport(symbol)
    print
    print "---- History ----"
    print "Equity Growth (%%)\t\t\t%s" % ("\t\t".join(msn_report.get_equities()))
    print "Sales Growth (%%)\t\t\t%s" % ("\t\t".join(msn_report.get_sales()))
    print "EPS Growth (%%)\t\t\t\t%s" % ("\t\t".join(msn_report.get_eps()))
    print "Cash flow Growth (%%)\t\t\t%s" % ("\t\t".join(msn_report.get_cashflow()))
    print "ROIC (%%)\t\t\t\t%s" % ("\t\t".join(msn_report.get_roic()))

    print "Analyst EPS Growth \t\t\t%s" % (msn_report.analyst_growth)
    print "Current EPS \t\t\t%s" % (msn_report.eps)
    print "Safe Price \t\t\t%s" % (msn_report.get_safe_price())
