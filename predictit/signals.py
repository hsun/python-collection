#!/usr/bin/env python

import sys, operator, csv
from debug import say
from optutil import get_opts
import yahoo
import reference
import sc
import fileutil
from mad import MadPicks

# this script gathers the signals from following sources:
#
#    http://www.stockcharts.com
#
# and writes the results into two files:
#
#     
class Scan(object):

    def __init__(self, data_dir):
        self.data_dir = data_dir

    def fetch_raw_signals(self):
        bulls = {}
        bears = {}

        sc_signals = sc.StockChartSignals()
        sc_signals.scan()
        bulls.update(sc_signals.bulls)
        bears.update(sc_signals.bears)

        self.write_raw_signal_file(bulls, "bull")
        self.write_raw_signal_file(bears, "bear")

    def write_raw_signal_file(self, signals, signal_file_base):
        # sort by the # of signals
        sorted_signals = sorted(signals.items(), key=lambda x: len(x[1]), reverse=True)
        writer = csv.writer(open("%s/%s" % (self.data_dir, fileutil.data_file_4_today(signal_file_base)), "w"))
        for symbol, signals in sorted_signals:
            writer.writerow([symbol] + signals)

if __name__ == '__main__':

    scan = Scan("work")
    scan.fetch_raw_signals()
    
    #scan = MadPicks("static")
    #scan.scan()
