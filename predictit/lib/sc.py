#!/usr/bin/env python

import sys, operator
from BeautifulSoup import BeautifulSoup
from debug import say
from optutil import get_opts
from siteutil import Site

#
# This script fetches the daily signals from http://www.stockcharts.com.
#
class StockChartSignals(object):

    HOST = "stockcharts.com"
    PORT = 80
    MIN_PRICE = 10.0
    MIN_VOLUME = 1000000.0
 
    # summary of the signals
    SIGNAL_SUMMARY_PAGE = "/def/servlet/SC.scan?s=runreport,predefall"

    # interested exchanges
    EXCHANGES = ["NASD", "NYSE", "AMEX"]

    # each identifies the description of a specific signal
    BULL_CANDLES = [
        "&nbsp; Bullish Engulfing",
        "&nbsp; Piercing Line",
        "&nbsp; Morning Star",
        "&nbsp; Rising Three Methods",
        "&nbsp; Dragonfly Doji",
        "&nbsp; Hammer",
        "Breakaway Gap Ups",
        "Runaway Gap Ups",
    ]
    BEAR_CANDLES = [
        "&nbsp; Bearish Engulfing",
        "&nbsp; Evening Star",
        "&nbsp; Falling Three Methods",
        "&nbsp; Gravestone Doji",
        "&nbsp; Shooting Star",
        "Breakaway Gap Downs",
        "Runaway Gap Downs",
    ]

    # below are some other signals available from the site
    BULL_SIGNALS = [
        "New 52-week Highs",
        "Strong Volume Gainers",
        "Bullish 50/200-day MA Crossovers",
        "Bullish MACD Crossovers",
        "Improving Chaikin Money Flow",
        "New CCI Buy Signals",
        "Parabolic SAR Buy Signals",
        "Stocks in a New Uptrend (Aroon)",
        "Stocks in a New Uptrend (ADX)",
        "Gap Ups",
        "Runaway Gap Ups",
        "&nbsp; Piercing Line",
        "&nbsp; Bullish Harami",
        "&nbsp; Dragonfly Doji",
        "&nbsp; Hammer",
        "P&amp;F Bullish Signal Reversal Alerts",
        "P&amp;F Bullish Catapult Alerts",
        "P&amp;F Bullish Triangle Alerts",
        "Oversold with an Improving RSI",
        "Moved Below Lower Bollinger Band",
        "Breakaway Gap Ups",
        "Island Bottoms",
        "&nbsp; Bullish Engulfing",
        "&nbsp; Morning Star",
        "&nbsp; Three White Soldiers",
    ]

    BEAR_SIGNALS = [
        "Overbought with a Declining RSI",
        "Moved Above Upper Bollinger Band",
        "Runaway Gap Downs",
        "&nbsp; Dark Cloud Cover",
        "&nbsp; Bearish Harami",
        "&nbsp; Filled Black Candles",
        "New 52-week Lows",
        "Strong Volume Decliners",
        "Bearish 50/200-day MA Crossovers",
        "Bearish MACD Crossovers",
        "Declining Chaikin Money Flow",
        "New CCI Sell Signals",
        "Parabolic SAR Sell Signals",
        "Stocks in a New Downtrend (Aroon)",
        "Stocks in a New Downtrend (ADX)",
        "Island Tops",
        "Breakaway Gap Downs",
        "&nbsp; Bearish Engulfing",
        "&nbsp; Evening Star",
        "&nbsp; Three Black Crows",
        "&nbsp; Gravestone Doji",
        "&nbsp; Shooting Star",
        "P&amp;F Bearish Signal Reversal Alerts",
        "P&amp;F Bearish Catapult Alerts",
        "P&amp;F Bearish Triangle Alerts",
    ]


    def __init__(self):

        self.site = Site(self.HOST, self.PORT)
        self.signal_paths = {}
        self.bulls = {}
        self.bears = {}
        
    def scan(self):
        self.load_signal_paths()
        self.load_signals(self.BULL_SIGNALS, self.bulls)
        self.load_signals(self.BEAR_SIGNALS, self.bears)

    def load_signal_paths(self):
        print "Start to load signal paths..."
        raw = self.site.fetch(self.SIGNAL_SUMMARY_PAGE)
        soup = BeautifulSoup(raw)
        signal = "N/A"
        try:
            rows = soup.findAll("tr", {"class":"odd"}) + soup.findAll("tr", {"class":"even"})
            for row in rows:
                fields = row.findAll("td")
                signal = fields[0].string
                if signal is not None:
                    signal_path = fields[6].a['href']
                    symbol_count = int(fields[6].a.string)
                    if symbol_count > 0:
                        self.signal_paths[signal] = signal_path
                    else:
                        print "Skip signal %s as its count is ZERO" % (signal)
        except Exception, e:
            print "Failed processing signal paths %s: %s" % (signal, e)
        print "Loaded signal paths"

    def load_signals(self, signals, results):
        for signal in signals:
            if self.signal_paths.has_key(signal):
                signal_path = self.signal_paths[signal]
                self.load_signal(signal, signal_path, results)
            else:
                say("Skip signal %s as we cannot find the URL path to the signal page." % (signal))

    def load_signal(self, signal, signal_path, results):
        raw = self.site.fetch(signal_path)
        soup = BeautifulSoup(raw)
        logged = 0
        try:
            rows = soup.findAll("td", {"class" : "first chartoptionlinks"})
            
            print("Processing signal %s" % (signal))
            for row in rows:
                
                fields = row.parent.findAll("td")
                symbol = fields[1].b.string
                company = fields[2].string
                exchange = fields[3].string
                sector = fields[4].string
                price = float(fields[9].string)
                volume = float(fields[10].string)
                # skip symbols like GM.V
                if self.shall_process(symbol, exchange, sector, price, volume):
                    say("Found: %s - %s" % (symbol, company))
                    self.process_signal(symbol, signal, results)
                    logged = logged + 1
                    
            print "%d symbols processed with %d logged" % (len(rows), logged)
        except Exception, e:
            print "Failed processing signal %s at path %s: %s" % (signal, signal_path, e)
            
    def shall_process(self, symbol, exchange, sector, price, volume):
        # skip symbols like GM.V
        if symbol.find(".") == -1 \
            and price > StockChartSignals.MIN_PRICE and volume > StockChartSignals.MIN_VOLUME \
            and exchange in StockChartSignals.EXCHANGES:
            return True
        else:
            return False

    def process_signal(self, symbol, signal, results):
        if not results.has_key(symbol):
            results[symbol] = []
        results[symbol].append(signal)

if __name__ == '__main__':

    stockchart = StockChartSignals()
    stockchart.scan()
    print '-' * 40
    print stockchart.bulls
    print stockchart.bears
    print '-' * 40
