#!/usr/bin/env python

import csv, datetime

def data_file_4_today(base):
    today = datetime.date.today()
    return "%s_%d%02d%02d.csv" % (base, today.year, today.month, today.day)

def data_file_4_day(base, days_delta):
    today = datetime.date.today()
    delta = datetime.timedelta(days=days_delta)
    the_day = today + delta
    return "%s_%d%02d%02d.csv" % (base, the_day.year, the_day.month, the_day.day)
