#!/usr/bin/env python

import sys, operator, csv
from debug import say
from optutil import get_opts
import yahoo
import reference
import stockta
import fileutil
import eval

REWARD_RISK_RATIO_THRESHOLD = 2.0
ENTRY_LEVEL = 0.01
STOP_LEVEL = 0.02
RISK_CAPITAL = 2000.0
ALERT_LEVEL = 10
ALERT_THRESHOLD = 0.04

LONG = 1
SHORT = 2

class Risk(object):

    def __init__(self, work_dir, lfile, sfile):
        self.work_dir = work_dir
        self.sta = stockta.StockTa()
        self.long_file = open(lfile, "a")
        self.short_file = open(sfile, "a")

    def write2l(self, s):
        self.long_file.write(s + "\n")

    def write2s(self, s):
        self.short_file.write(s + "\n")

    def eval(self, symbol, pos):
        prices = self.sta.get_price_levels(symbol)
        print "Analyzing %s" % (symbol)
        if pos == LONG:
          if prices['support_level'] >= ALERT_LEVEL and prices['close'] < (1 + ALERT_THRESHOLD) * prices['support']:
            stop = (1 - STOP_LEVEL) * prices['support']
            min_entry = (1 + ENTRY_LEVEL) * prices['support']
            max_entry = (prices['resist'] + REWARD_RISK_RATIO_THRESHOLD * stop) / (1.0 + REWARD_RISK_RATIO_THRESHOLD)
            if max_entry > min_entry:
              self.calc_play(symbol, prices, min_entry, max_entry, stop, pos)
            else:
              print "No good entry level for long position"
          else:
            print "Close price is too high or support is too weak"
        elif pos == SHORT:
          if prices['resist_level'] >= ALERT_LEVEL and prices['close'] > (1 - ALERT_THRESHOLD) * prices['resist']:
            stop = (1 + STOP_LEVEL) * prices['resist']
            max_entry = (1 - ENTRY_LEVEL) * prices['resist']
            min_entry = (prices['support'] + REWARD_RISK_RATIO_THRESHOLD * stop) / (1.0 + REWARD_RISK_RATIO_THRESHOLD)
            if max_entry > min_entry:
              self.calc_play(symbol, prices, min_entry, max_entry, stop, pos)
            else:
              print "No good entry level for short positon"
          else:
            print "Close price is too low or resistance is weak"
        else:
          raise "Bad position param %s" % (pos)

    def calc_play(self, symbol, prices, min_entry, max_entry, stop, pos):
        if pos == LONG:
          shares_min = int(RISK_CAPITAL / (min_entry - stop))
          shares_max = int(RISK_CAPITAL / (max_entry - stop))
          ratio_min = (prices['resist'] - min_entry) / (min_entry - stop)
          ratio_max = (prices['resist'] - max_entry) / (max_entry - stop)
          play = "%s[%.2f - %d]:  low: [%.2f - %.0f - %.2f]  high: [%.2f - %.0f - %.2f] stop: %.2f" \
                % (symbol, prices['support'], prices['support_level'], min_entry, shares_min, ratio_min, max_entry, shares_max, ratio_max, stop)
          print play
          self.write2l(play)
        elif pos == SHORT:
          shares_min = int(RISK_CAPITAL / (stop - min_entry))
          shares_max = int(RISK_CAPITAL / (stop - max_entry))
          ratio_min = (prices['support'] - min_entry) / (min_entry - stop)
          ratio_max = (prices['support'] - max_entry) / (max_entry - stop)
          play = "%s[%.2f - %d]:  low: [%.2f - %.0f - %.2f]  high: [%.2f - %.0f - %.2f] stop: %.2f" \
                % (symbol, prices['resist'], prices['resist_level'], min_entry, shares_min, ratio_min, max_entry, shares_max, ratio_max, stop)
          print play
          self.write2s(play)
        else:
          raise "Bad position param %s" % (pos)

    def analyze_candidates(self, candidate_file, pos):
        reader = csv.reader(open(candidate_file, "r"))
        reader.next()
        for row in reader:
          try:
            self.eval(row[0], pos)
          except Exception, e:
            print "Failed to analyze %s: %s" % (row[0], e)

    def analyze_candidate(self, symbol, pos):
        try:
          self.eval(symbol, pos)
        except Exception, e:
          print "Failed to analyze %s: %s" % (symbol, e)
          
if __name__ == '__main__':

    risk = Risk("work", "work/long.txt", "work/short.txt")
    opts = get_opts({"s" : "symbol", "f" : "candidates", "m" : "mode"})
    if opts.get("mode") == "s":
        pos = SHORT
    elif opts.get("mode") == "l":
        pos = LONG
    else:
        pos = None
 
    if opts.get("candidates"):
        if pos:
            risk.analyze_candidates(opts["candidates"], pos)
        else:
            risk.analyze_candidates(opts["candidates"], LONG)
            risk.analyze_candidates(opts["candidates"], SHORT)
    elif opts.get("symbol"):
        if pos:
            risk.analyze_candidate(opts["symbol"], pos)
        else:
            risk.analyze_candidate(opts["symbol"], LONG)
            risk.analyze_candidate(opts["symbol"], SHORT)
    else:
        print "Invalid command line options"
