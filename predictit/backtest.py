#!/usr/bin/env python

import sys, os.path
import operator, csv, glob
import datetime
from optutil import get_opts
from debug import say
import fileutil
import yahoo

LONG = "bull"
SHORT = "bear"
MAX_HOLDING = 30
TRADE_RANGE = 0.015
BULL_SIGNALS = set([
    "Bullish 50/200-day MA Crossovers",
    "Bullish MACD Crossovers",
    "Gap Ups",
    "Runaway Gap Ups",
    "&nbsp; Piercing Line",
    "&nbsp; Bullish Harami",
    "&nbsp; Dragonfly Doji",
    "&nbsp; Hammer",
    "Breakaway Gap Ups",
    "Island Bottoms",
    "&nbsp; Bullish Engulfing",
    "&nbsp; Morning Star",
    "&nbsp; Three White Soldiers",
])

BEAR_SIGNALS = set([
    "Runaway Gap Downs",
    "&nbsp; Dark Cloud Cover",
    "&nbsp; Bearish Harami",
    "&nbsp; Filled Black Candles",
    "Bearish 50/200-day MA Crossovers",
    "Bearish MACD Crossovers",
    "Island Tops",
    "Breakaway Gap Downs",
    "&nbsp; Bearish Engulfing",
    "&nbsp; Evening Star",
    "&nbsp; Three Black Crows",
    "&nbsp; Gravestone Doji",
    "&nbsp; Shooting Star",
])

# ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Clos'],
def high(quote):
    return float(quote[2])

def low(quote):
    return float(quote[3])

def _open(quote):
    return float(quote[1])

def _close(quote):
    return float(quote[4])

def volume(quote):
    return float(quote[5])

def add_workdays(adate, nworkdays):
    if nworkdays < 0:
        incr = -1
        nworkdays = - nworkdays
    else:
        incr = 1
    delta_weeks, delta_days = divmod(nworkdays, 5)
    one_day = datetime.timedelta(days=incr)
    if delta_weeks:
        wdate = adate + one_day * 7 * delta_weeks
    else:
        wdate = adate
    while delta_days:
        wdate += one_day
        if wdate.weekday() < 5: # Mon-Fri
            delta_days -= 1
    return wdate

def get_end_date(start_date):
    sdate = datetime.datetime.strptime(start_date, '%Y%m%d').date()
    edate = add_workdays(sdate, MAX_HOLDING)
    today = datetime.date.today()
    if today > edate:
        return edate.strftime('%Y%m%d')
    else:
        return today.strftime('%Y%m%d')

class BackTest(object):

    winners = {}
    losers = {}
    profits = {}
    
    def __init__(self, data_dir, static_dir):
        self.data_dir = data_dir
        self.static_dir = static_dir
        
    def load_symbols(self, file_base):
        return self.load_raw_file(file_base)

    def load_csv_file(self, file_name):
        data = {}
        f = "%s/%s" % (self.data_dir, file_name)
        if not os.path.isfile(f):
            raise Exception("File %s does not exist." % file_name)

        say("Load data from file %s" % (f))
        reader = csv.reader(open(f, "r"))
        for row in reader:
            data[row[0]] = (row[1:])
        return data
    
    def measure_success(self, candidates, start_date, end_date, position):
        
        def register_profit(profit, signals):
            for signal in signals:
                total_profit = self.profits.setdefault(signal, 0.0)
                self.profits[signal] = (total_profit + profit)

                if profit > 0.0:
                    self.losers.setdefault(signal, 0)
                    count = self.winners.setdefault(signal, 0)
                    self.winners[signal] = (count + 1)
                else:
                    self.winners.setdefault(signal, 0)
                    count = self.losers.setdefault(signal, 0)
                    self.losers[signal] = (count + 1)

        def is_in_trade_range(close_price, open_price):
            delta = abs((close_price - open_price) / open_price)
            say("Delta is %.2f" % delta)
            return delta <= TRADE_RANGE

        def get_my_signals(signals, position):
            if position == LONG:
                my_signals = list(BULL_SIGNALS.intersection(signals))
                if len(my_signals) > 0:
                    return my_signals
            else:
                my_signals = list(BEAR_SIGNALS.intersection(signals))
                if len(my_signals) > 0:
                    return my_signals
            return None
        
        # historic quotes
        def is_a_trade(historic_quotes, position):
            start_day_close = _close(historic_quotes[0])
            next_day_open = _open(historic_quotes[1])
            
            if position == LONG:
                say("LONG: %.2f %.2f" % (start_day_close, next_day_open))
                return next_day_open >= start_day_close and is_in_trade_range(start_day_close, next_day_open)
            else:
                say("SHORT: %.2f %.2f" % (start_day_close, next_day_open))
                return next_day_open <= start_day_close and is_in_trade_range(start_day_close, next_day_open)
 
        def get_profit(historic_quotes, position):
            acquired_price = _open(historic_quotes[1])
            exit_price = acquired_price
            previous_day_low = low(historic_quotes[0])
            previous_day_high = high(historic_quotes[0])
            for quote in historic_quotes[1:]:
                if position == LONG:
                    today_low = low(quote)
                    if today_low < (previous_day_low - 0.01):
                        exit_price = previous_day_low
                        break
                    else:
                        previous_day_low = today_low
                        exit_price = _close(quote)
                else:
                    today_high = high(quote)
                    if today_high > (previous_day_high + 0.01):
                        exit_price = previous_day_high
                        break
                    else:
                        previous_day_high = today_high
                        exit_price = _close(quote)
            if position == LONG:
                return (exit_price - acquired_price) / acquired_price
            else:
                return (acquired_price - exit_price) / acquired_price
        
        for symbol, signals in candidates.items():
            
            my_signals = get_my_signals(signals, position)
            if my_signals is None:
                say("Skip symbol %s for non-interested signals %s " % (symbol, signals))
                continue
            
            try:
                historic_quotes = yahoo.get_historical_prices(symbol, start_date, end_date)[1:]
                if historic_quotes:
                    if is_a_trade(historic_quotes, position):
                        profit = get_profit(historic_quotes, position)
                        say("Register profit for %s" % symbol)
                        register_profit(profit, my_signals)
                    else:
                        say("Skip symbol %s as it is out trading range " % (symbol))
                else:
                    print "No historic data for %s" % symbol
            except Exception, e:
                print "Failed to evaluate %s due to %s" % (symbol, e)     
    
    def find_success_rate_for_position(self, start_date, end_date, position):
        candidates = self.load_csv_file("%s_%s.csv" % (position, start_date))
        print ">>Evaluating %s out of %d candidates." % (position, len(candidates))
        self.measure_success(candidates, start_date, end_date, position)

    def report_final_scores(self):
        print ">> Report winners:"
        sorted_scores = sorted(self.profits.items(), key=lambda x: x[1], reverse=True)
        for signal, profit in sorted_scores:
            print "%s [%d - %d]: %.2f" % (signal, self.winners[signal], self.losers[signal], profit)

    def test_success_rate(self, start_date, end_date):
        
        def market_status():
            market_symbol = 'SPY'
            market_quotes = yahoo.get_historical_prices(market_symbol, start_date, end_date)[1:]
            market_direction = _close(market_quotes[0]) > _close(market_quotes[-1])
            cur_quotes = yahoo.get_all(market_symbol)
            above_200ma = cur_quotes['price'] > cur_quotes['200day_moving_avg']
            above_50ma = cur_quotes['price'] > cur_quotes['50day_moving_avg']
            ma50_above_ma200 = cur_quotes['50day_moving_avg'] > cur_quotes['200day_moving_avg']
            print "For period from %s to %s" % (start_date, end_date)
            print "SP 500 is %s " % ("UP" if market_direction else "DOWN")
            print "Current price level is %s its 50 MA" % ("above" if above_50ma else "below") 
            print "Current price level is %s its 200 MA" % ("above" if above_200ma else "below") 
            print "Current 50 MA is %s 200 MA" % ("above" if ma50_above_ma200 else "below") 
            print
        
        # market_status()
        print "\nWorking on date set from %s to %s" % (start_date, end_date)
        self.find_success_rate_for_position(start_date, end_date, LONG)
        self.find_success_rate_for_position(start_date, end_date, SHORT)

    def test_success_rates(self):
        signal_files = glob.glob("%s/bull*" % (self.data_dir))
        dateset = sorted([x.split('_')[1].split('.')[0] for x in signal_files])
        for start_date in dateset:
            end_date = get_end_date(start_date)
            self.test_success_rate(start_date, end_date)
        self.report_final_scores()


if __name__ == '__main__':

    monitor = BackTest("work", "static")
    monitor.test_success_rates()
