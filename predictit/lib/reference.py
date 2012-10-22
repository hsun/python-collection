#!/usr/bin/env python

import csv, datetime

class References(object):

    _company_names = {}
    _company_sizes = {}
    _industry_names = {}
    _company_industry = {}
    _high_ranked = []

    def __init__(self, base):
        companies = csv.reader(open("%s/company.csv" % (base)))
        for row in companies:
            self._company_names[row[0]] = row[2]
            self._company_sizes[row[0]] = float(row[1])

        industries = csv.reader(open("%s/industry.csv" % (base)))
        for row in industries:
            self._industry_names[row[0]] = row[1]

        company_industry_mappings = csv.reader(open("%s/company-industry.csv" % (base)))
        for row in company_industry_mappings:
            self._company_industry[row[0]] = row[1]

        ranked = csv.reader(open("%s/stock_scouter.csv" % (base)))
        self._high_ranked = [x[0] for x in ranked]

    def get_company_name(self, symbol):
        return self._company_names.get(symbol)

    def get_company_size(self, symbol):
        return self._company_sizes.get(symbol)

    def get_company_industry(self, symbol):
        return self._company_industry.get(symbol)

    def get_industry_name(self, code):
        return self._industry_names.get(code)

    def is_high_ranked(self, symbol):
        return symbol in self._high_ranked

    def is_low_ranked(self, symbol):
        # for now
        return True

if __name__ == '__main__':

    reference = References("../static")
    print "Company name for symbol %s is: %s " % ("INTU", reference.get_company_name("INTU"))
    print "Company size for symbol %s is: %s " % ("INTU", reference.get_company_size("INTU"))
    print "Company name for symbol %s is: %s " % ("INTU", reference.get_company_industry("INTU"))
    print "Industry name for code %s is: %s " % ("821", reference.get_industry_name("821"))
    print "%s is high ranked?: %s " % ("OKS", reference.is_high_ranked("OKS"))
