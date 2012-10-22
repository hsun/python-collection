#!/usr/bin/env python

import sys, operator, csv
from statlib import stats
from debug import say
import yahoo
import stockta

class Evaluator(object):

    RISK_THRESHOLD = 0.05
    LOSS_THRESHOLD = 450.0
    MAX_BUY = 5000.00
    WEIGHT = 2
    
    def evaluate_bull(self, symbol, meta):
        pazz = False
        msg = None
        try:
            prices = self.stockta.get_price_levels(symbol)
            stop_loss = (prices['close'] + prices['open'])/2.0
            buy_stop = prices['close']
            buy_limit = buy_stop + prices['close'] * 0.005
            
            if prices['resist'] is None:
                # no resistance - good
                pazz = True
                msg = "No strong resistance"
            elif prices['resist'] < buy_stop:
                # no support, bad
                pazz = True
                msg = "Above resistance"
            else:
                upside = (prices['resist'] - buy_limit) / buy_limit 
                if upside > self.RISK_THRESHOLD:
                    # just approximate
                    shares = int(self.LOSS_THRESHOLD / (buy_limit - stop_loss))
                    if shares * buy_limit > self.MAX_BUY:
                        shares = int(self.MAX_BUY / buy_limit)
                    msg = "Shares: %d, stop loss: %.2f, buy stop: %.2f, buy limit: %.2f" %\
                        (shares, stop_loss, buy_stop, buy_limit)
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
            stop_loss = (prices['close'] + prices['open'])/2.0
            sell_stop = prices['close']
            sell_limit = sell_stop - prices['close'] * 0.005
            
            if prices['support'] is None:
                # no support - good
                pazz = True
                msg = "No strong support"
            elif prices['support'] < sell_stop:
                # below support, good
                pazz = True
                msg = "Below support"
            else:
                downside = (sell_limit - prices['support']) / sell_limit 
                if downside > self.RISK_THRESHOLD:
                    # just approximate
                    shares = int(self.LOSS_THRESHOLD / (stop_loss - sell_limit))
                    if shares * sell_limit > self.MAX_BUY:
                        shares = int(self.MAX_BUY / sell_limit)
                    msg = "Shares: %d, stop loss: %.2f, sell stop: %.2f, sell limit: %.2f" %\
                        (shares, stop_loss, sell_stop, sell_limit)

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
