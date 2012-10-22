#!/usr/bin/env python

import sys, operator, csv, os.path
from statlib import stats
from debug import say
from optutil import get_opts
import yahoo
import fileutil
import reference
import eval_price_volume, eval_candlestick_risk, eval_mad

class Analyzor(object):

    BASE_PATH_CHART = "http://stockcharts.com/scripts/php/candleglance.php?%s|C|L14"
    LONG = 0
    SHORT = 1

    def __init__(self, data_dir, static_dir):
        self.data_dir = data_dir
        self.static_dir = static_dir
        self.evaluators = [
            eval_price_volume.Evaluator(self.data_dir, self.static_dir),
            eval_mad.Evaluator(self.data_dir, self.static_dir),
            eval_candlestick_risk.Evaluator(self.data_dir, self.static_dir),
            ]

    def analyze(self):
        bulls = {}
        bears = {}

        tech_bulls, days_delta = self.load_raw_signals("bull")
        bulls.update(tech_bulls)
        tech_bears, days_delta = self.load_raw_signals("bear")
        bears.update(tech_bears)
        
        print "Working on bull signals"
        for bull in bulls:
            for evaluator in self.evaluators:
                if bulls[bull]['weight'] > 0:
                    evaluator.evaluate_bull(bull, bulls)

        print "Working on bear signals"
        for bear in bears:
            for evaluator in self.evaluators:
                if bears[bear]['weight'] > 0:
                    evaluator.evaluate_bear(bear, bears)

        print "Reporting bulls"
        self.report(bulls, self.LONG, "long")
        print "Reporting bears"
        self.report(bears, self.SHORT, "short")

    def load_raw_signals(self, file_base, days_delta = None):
        data = {}
        try:
            f = "NA"
            if not days_delta:
                f = "%s/%s" % (self.data_dir, fileutil.data_file_4_today(file_base))
            else:
                found = False
                while not found:
                    f = "%s/%s" % (self.data_dir, fileutil.data_file_4_day(file_base, days_delta))
                    if not os.path.isfile(f):
                        days_delta = days_delta - 1
                    else:
                        found = True

            reader = csv.reader(open(f, "r"))
            for row in reader:
                data[row[0]] = {'pattern': row[1:], 'eval': [], 'weight': 1}
        except Exception, e:
            print "Failed to load file %s: %s" % (f, e)      
        return data, days_delta
    
    def report(self, symbols, type, file_base):
        # sort by the # of signals
        sorted_symbols = sorted(symbols.items(), key=lambda x: x[1]['weight'], reverse=True)
        writer = open("%s/%s" % (self.data_dir, fileutil.data_file_4_today(file_base)), "w")
        reported = []
        for symbol, meta in sorted_symbols:
            if meta['weight'] > 0:
                reported.append(symbol)
                self.write(writer, "%s [%s:%d]: %s" % (symbol, ",".join(meta['pattern']), meta['weight'], ";".join(meta['eval'])))
        while len(reported) > 10:
            self.write(writer, self.BASE_PATH_CHART % ",".join(reported[:10]))
            reported = reported[10:]
        self.write(writer, self.BASE_PATH_CHART % ",".join(reported))

    def write(self, w, m):
        print m
        w.write(m + "\n")

if __name__ == '__main__':

    scan = Analyzor("work", "static")
    scan.analyze()
