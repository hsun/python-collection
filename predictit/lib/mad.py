#!/usr/bin/env python

import sys, operator, re, urllib, csv
from BeautifulSoup import BeautifulSoup
from mechanize import Browser

from siteutil import Site
from debug import say
from optutil import get_opts

class MadPicks(object):

    HOST = "madmoney.thestreet.com"
    PORT = 80
    STOCK_PICK_REPORT = "/screener/index.cfm?showview=stocks&showrows=500"
    SYMBOL_PATTERN = re.compile(r".+quote/(\w+)\.html.+")

    def __init__(self, static_dir):

        self.static_dir = static_dir
        self.site = Site(self.HOST, self.PORT)
        
    def scan(self):
        print "Working on bulls"
        self.write_file("mad_bull.csv", self.load_data("buy"))
        print "Working on bears"
        self.write_file("mad_bear.csv", self.load_data("sell"))

    def load_data(self, recommandation):
        
        if "buy" == recommandation:
            called = "5"
        elif "sell" == recommandation:
            called = "1"
        else:
            called = "%"
        
        br = Browser()
        br.open("http://%s:%d%s" % (self.HOST, self.PORT, self.STOCK_PICK_REPORT))
        br.select_form(name="stocksForm")
        br["airdate"] = ['30']
        br["called"] = [called]
        br["industry"] = ['%']
        br["sector"] = ['%']
        br["segment"] = ['%']
        br["pricelow"] = ['10']
        br["pricehigh"] = ['1000']
        br["sortby"] = ['airdate']
        response = br.submit()  # submit current form
        return self.extract_symbols(response.read())

    def extract_symbols(self, raw):
        data = {}
        soup = BeautifulSoup(raw)
        try:
            trs = soup.findAll("tr", attrs={"class" : "odd"}, recursive=True)
            for tr in trs:
                cols = tr.findAll("td")
                m = re.match(self.SYMBOL_PATTERN, cols[0].find("a")['href'])
                if m:
                    symbol = m.group(1)
                    if not data.has_key(symbol):
                        data[symbol] = cols[1].string
        except Exception, e:
            print "Failed to extract symbols: %s" % (e)
        print "Extracted %d symbols" % (len(data))
        return data
    
    def write_file(self, file, data):
        writer = csv.writer(open("%s/%s" % (self.static_dir, file), "w"))
        for row in data:
            writer.writerow([row, data[row]])

if __name__ == '__main__':

    st = MadPicks("../static")
    st.scan()
