#!/usr/bin/env python

import sys, operator, csv, os.path
from statlib import stats
from debug import say
from optutil import get_opts
import yahoo
import reference
import bighat
import sc
import fileutil

class Monitor(object):

    RISK_CAPITAL = 1000.0
    MARKET = "SPY"
    SECTORS = ["Basic Materials", "Conglomerates", "Consumer Goods", "Financial", "Healthcare", \
               "Industrial Goods", "Services", "Technology", "Utilities"]
    SECTOR_INDEX = ["XLB", "MMM", "IYC", "XLF", "XLY", "XLI", "IYC", "XLK", "XLU"]

    def __init__(self, data_dir, static_dir):
        self.data_dir = data_dir
        self.static_dir = static_dir
        self.sector_trends = []
        self.get_sector_trends()
        
    def get_sector_trends(self):
        for sector in self.SECTOR_INDEX:
            change = float(yahoo.get_all(sector)['change'])
            print "Sector fund %s: %.2f" % (sector, change)
            if change > 0.0:
                self.sector_trends.append('UP')
            else:
                self.sector_trends.append('DOWN')

    def check(self):
        try:
            market_trend_up = self.is_market_up()
            if market_trend_up:
                data = self.load_symbols('top_companies')
            else:
                data = self.load_symbols('bot_companies')
            for symbol in data.keys():
                d = data[symbol]
                sector = d[0]
                midpoint = float(d[1])
                support = float(d[4])
                resist = float(d[5])
                if self.is_sector_in_sync(market_trend_up, sector):
                    self.eval(symbol, market_trend_up, midpoint, support, resist)
        except Exception, e:
            print e
        print "Done.."
        
    def is_market_up(self):
        return float(yahoo.get_all(self.MARKET)['change']) > 0
        
    def is_sector_in_sync(self, market_trend_up, sector):
        if market_trend_up:
            return self.sector_trends[self.SECTORS.index(sector)] == 'UP'
        else:
            return self.sector_trends[self.SECTORS.index(sector)] == 'DOWN'
        
    def load_symbols(self, file_base):
        return self.load_raw_file(file_base)

    def load_raw_file(self, file_base, days_delta = 0):
        data = {}
        try:
            f = "NA"
            found = False
            while not found:
                f = "%s/%s" % (self.data_dir, fileutil.data_file_4_day(file_base, days_delta))
                if not os.path.isfile(f):
                    days_delta = days_delta - 1
                else:
                    found = True
            print "Load data from file %s" % (f)
            reader = csv.reader(open(f, "r"))
            for row in reader:
                data[row[0]] = (row[4:10])
        except Exception, e:
            print "Failed to load file %s: %s" % (f, e)      
        return data

    def eval(self, symbol, trend_up, midpoint, support, resist):
        try:
            quote = float(yahoo.get_all(symbol)['price'])
            odds = 0.0
            gap = 0.0
            if trend_up:
                stop = max(midpoint, support)
                if quote > stop:
                    odds = (resist - quote) / (quote - stop) 
                    gain = (resist - quote) / quote * 100.0
                    gap = (quote - stop) /quote * 100.0
                    shares = min(500, int(self.RISK_CAPITAL / (quote - stop)))
            else:
                stop = min(midpoint, resist)
                if quote < stop:
                    odds = (quote - support) / (stop - quote) 
                    gain = (quote - support) / quote * 100.0
                    gap = (stop - quote) /quote * 100.0
                    shares = min(500, int(self.RISK_CAPITAL / (stop - quote)))

            if odds > 3.0 and gap > 0.5:
                print "%s: %.2f, %.2f, %.2f, %.2f, %.2f, %.2f" % (symbol, odds, gap, gain, shares, quote, stop)
                
        except Exception, e:
            print "Failed to evaluate %s: %s " % (symbol, e)
        return (0, 0, 0, 0, 0)

if __name__ == '__main__':

    monitor = Monitor("work", "static")
    monitor.check()
