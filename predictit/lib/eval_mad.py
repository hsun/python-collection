#!/usr/bin/env python

import sys, operator, csv
from statlib import stats
from debug import say

class Evaluator(object):
    
    WEIGHT = 1

    def evaluate(self, symbol, meta, potentials):
        try:
            if symbol in potentials:
                print "Mentioned by Mad: %s" % (symbol)
                meta[symbol]['eval'].append("Mentioned by mad")
                meta[symbol]['weight'] = meta[symbol]['weight'] + self.WEIGHT
            else:
                say("Skip symbol %s for missing from Mad." % (symbol))
        except Exception, e:
            print "Failed to evaluate Mad index for symbol %s: %s" % (symbol, e)
    
    def evaluate_bull(self, bull, bulls):
        potential_bulls = self.load_mad_meta("mad_bull.csv")
        self.evaluate(bull, bulls, potential_bulls)

    def evaluate_bear(self, bear, bears):
        potential_bears = self.load_mad_meta("mad_bear.csv")
        self.evaluate(bear, bears, potential_bears)

    def load_mad_meta(self, file):
        data = []
        try:
            f = "%s/%s" % (self.static_dir, file)
            reader = csv.reader(open(f, "r"))
            for row in reader:
                if row != None and len(row) > 0:
                    data.append(row[0])
        except Exception, e:
            print "Failed to load file %s: %s" % (f, e)      
        return data

    def __init__(self, data_dir, static_dir):
        self.static_dir = static_dir
