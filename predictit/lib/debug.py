#!/usr/bin/env python

import os

def say(s):
    if os.environ.has_key('DEBUGP'):
        print s

if __name__ == '__main__':

    print "To see output, make sure debug is on: export DEBUGP=1"
    say("Hello, Say you say me.")
