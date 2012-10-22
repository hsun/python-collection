#!/usr/bin/env python

import sys, operator, csv
from statlib import stats
from debug import say
import yahoo
import stockta

class Evaluator(object):

    ODDS_THRESHOLD = 3.0
    LOSS_THRESHOLD = 450.0
    MAX_BUY = 5000.00
    WEIGHT = 2
    
    def evaluate_bull(self, symbol, meta):
        pazz = False
        msg = None
        try:
            prices = self.stockta.get_price_levels(symbol)
            if prices['resist'] is None:
                # no resistance - good
                pazz = True
                msg = "No strong resistance"
            elif prices['support'] is None:
                # no support, bad
                pazz = False
            else:
                upside = prices['resist'] - prices['high']
                downside = prices['high'] - prices['support']
                odds = upside/downside
                if odds > self.ODDS_THRESHOLD:
                    # just approximate
                    shares = int(self.LOSS_THRESHOLD / downside)
                    if shares * prices['close'] > self.MAX_BUY:
                        shares = int(self.MAX_BUY / prices['close'])
                    gain = shares * upside
                    loss = shares * downside
                    msg = "High odds: Odds: %.2f, Shares: %d, Gain: %.2f, Loss: %.2f" %\
                        (odds, shares, gain, loss)
            if pazz:
                print "Accept %s for its low risk"  % (symbol)
                meta[symbol]['eval'].append("Low Risk: " + msg)
                meta[symbol]['weight'] = meta[symbol]['weight'] + self.WEIGHT
            else:
                print "Reject %s for its high risk"  % (symbol)
                meta[symbol]['weight'] = -1000
        except Exception, e:
            print "Failed to evaluate risk for symbol %s: %s" % (symbol, e)
            meta[symbol]['weight'] = -1000

    def evaluate_bear(self, symbol, meta):
        pazz = False
        msg = None
        try:
            prices = self.stockta.get_price_levels(symbol)
            if prices['support'] is None:
                # no support - good
                pazz = True
                msg = "No strong support"
            elif prices['resist'] is None:
                # no resist, bad
                pazz = False
            else:
                upside = prices['low'] - prices['support']
                downside = prices['resist'] - prices['low']
                odds = upside/downside
                if odds > self.ODDS_THRESHOLD:
                    # just approximate
                    shares = int(self.LOSS_THRESHOLD / downside)
                    if shares * prices['close'] > self.MAX_BUY:
                        shares = int(self.MAX_BUY / prices['close'])
                    gain = shares * upside
                    loss = shares * downside
                    msg = "High odds: Odds: %.2f, Shares: %d, Gain: %.2f, Loss: %.2f" %\
                        (odds, shares, gain, loss)
            if pazz:
                print "Accept %s for its low risk"  % (symbol)
                meta[symbol]['eval'].append("Low Risk: " + msg)
                meta[symbol]['weight'] = meta[symbol]['weight'] + self.WEIGHT
            else:
                print "Reject %s for its high risk"  % (symbol)
                meta[symbol]['weight'] = -1000
        except Exception, e:
            print "Failed to evaluate risk for symbol %s: %s" % (symbol, e)
            meta[symbol]['weight'] = -1000

    def __init__(self, data_dir, static_dir):
        self.stockta = stockta.StockTa()
