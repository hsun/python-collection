#!/usr/bin/env python

import sys, operator, csv
from statlib import stats
from debug import say
import yahoo

class Evaluator(object):

    VOLUME_THRESHOLD = 1.1
    PRICE_CHANGE_THRESHOLD = 0.03
    SHORT_RATIO_LOW_THRESHOLD = 1.0
    SHORT_RATIO_HIGH_THRESHOLD = 4.0
    WEIGHT = 2
    
    def evaluate_bull(self, symbol, meta):
        try:
            data = yahoo.get_all(symbol)
            price = data['price']
            change = data['change']
            volume = data['volume']
            avg_volume = data['avg_daily_volume']
            moving_average_50 = data['50day_moving_avg']
            short_ratio = data['short_ratio']
            if (volume is None or avg_volume is None or volume > avg_volume * self.VOLUME_THRESHOLD) \
                and (moving_average_50 is None or price > moving_average_50) \
                and (price is None or change is None or change/price < self.PRICE_CHANGE_THRESHOLD):
                print "Accept %s for its price volume pattern"  % (symbol)
                meta[symbol]['eval'].append("Price Volume Pattern")
                meta[symbol]['weight'] = meta[symbol]['weight'] + self.WEIGHT
            else:
                print "Reject %s for its price volume pattern: Change: %.2f Volume: %.2f Avg Volume: %.2f Price: %.2f MA: %.2f Short Ratio: %.2f"\
                  % (symbol, change or 0.0, volume or 0.0, avg_volume or 0.0, price or 0.0, moving_average_50 or 0.0, short_ratio or 0.0)
                meta[symbol]['weight'] = -1000
        except Exception, e:
            print "Failed to evaluate price volume pattern for symbol %s: %s" % (symbol, e)

    def evaluate_bear(self, symbol, meta):
        try:
            data = yahoo.get_all(symbol)
            price = data['price']
            change = data['change'] * -1.0
            moving_average_50 = data['50day_moving_avg']
            short_ratio = data['short_ratio']
            # volume is less important for price dropping 
            if (price is None or change is None or change/price < self.PRICE_CHANGE_THRESHOLD) \
                    and (moving_average_50 is None or price < moving_average_50) :
                print "Accept %s for its price volume pattern"  % (symbol)
                meta[symbol]['eval'].append("Price Volume Pattern")
                meta[symbol]['weight'] = meta[symbol]['weight'] + self.WEIGHT
            else:
                print "Reject %s for its price volume pattern: Change: %.2f Price: %.2f MA: %.2f Short Ratio: %.2f"\
                  % (symbol, change or 0.0, price or 0.0, moving_average_50 or 0.0, short_ratio or 0.0)
                meta[symbol]['weight'] = -1000
        except Exception, e:
            print "Failed to evaluate price volume pattern for symbol %s: %s" % (symbol, e)

    def __init__(self, data_dir, static_dir):
        pass
