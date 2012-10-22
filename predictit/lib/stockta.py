#!/usr/bin/env python

import sys, operator, re, time
from siteutil import Site
from BeautifulSoup import BeautifulSoup
from debug import say
from optutil import get_opts

class StockTa(object):

    HOST = "www.stockta.com"
    PORT = 80
    ANALYSIS_PATH = "/cgi-bin/analysis.pl?symb=%s"
    THRESHOLD = 5

    def __init__(self):
        self.site = Site(self.HOST, self.PORT)
        self.cache = {}

    def get_price_levels(self, symbol):

        prices = self.cache.get(symbol)
        if prices:
          return prices
        path = self.ANALYSIS_PATH % (symbol)
        raw = self.site.fetch(path)
        soup = BeautifulSoup(raw)
        try:
            summary = soup.body.find("td", text="Last Trade").parent.parent.parent.findAll("tr")[1].findAll("td")
            prices = {}
            prices['open'] = float(summary[4].string)
            prices['close'] = float(summary[1].font.string)
            prices['low'] = float(summary[6].string)
            prices['high'] = float(summary[5].string)

            prices['resist'] = self.find_resist(soup)
            prices['support'] = self.find_support(soup)
            self.cache[symbol] = prices
            return prices
        except Exception, e:
            print "Failed to get price levels for %s: %s" % (symbol, e)
            return {}

    def find_resist(self, soup):
        try:
            resist_price = None
            levels = soup.body.find("font", text="resist.").parent.parent.parent.parent.findAll("tr")[1:]
            for level in levels:
                cols = level.findAll("td")
                level_type = cols[0].font.string
                level_price = float(cols[1].font.string)
                level_strength = int(cols[2].font.string)
                if level_strength >= self.THRESHOLD:
                    if "resist." == level_type:
                        resist_price = level_price
            return resist_price
        except Exception, e:
            print "Failed to get resistance level: %s" % (e)
            return None

    def find_support(self, soup):
        try:
            support_price = None
            levels = soup.body.find("font", text="supp").parent.parent.parent.parent.findAll("tr")[1:]
            for level in levels:
                cols = level.findAll("td")
                level_type = cols[0].font.string
                level_price = float(cols[1].font.string)
                level_strength = int(cols[2].font.string)
                if level_strength >= self.THRESHOLD:
                    if "supp" == level_type and support_price is None:
                        support_price = level_price
            return support_price
        except Exception, e:
            print "Failed to get support level: %s" % (e)
            return None

if __name__ == '__main__':

    sta = StockTa()
    print sta.get_price_levels("BBY")
    print "-" * 40
