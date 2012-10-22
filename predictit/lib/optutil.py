#!/usr/bin/env python

import getopt, sys

def get_opts(opt_conf):

    opt_conf_str = ''.join([x + ":" for x in opt_conf.keys()])
    opt_values = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], opt_conf_str)
    except getopt.GetoptError:
        print "Invalid command line options: " + " ".join(sys.argv[1:])
        sys.exit(2)

    for opt, arg in opts:
        opt =  opt[1:]
        opt_values[opt_conf[opt]] = arg
    return opt_values

if __name__ == '__main__':

    print "Try args: -s abc -t single -v true"
    print get_opts({"s" : "symbol", "t" : "type", "v" : "Verbos"})

