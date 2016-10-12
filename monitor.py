#!/usr/bin/env python
# encoding=utf8

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import time
from argparse import ArgumentParser
from core import EdcMonitor

''' 监控
    
    python monitor.py --tick=3
'''


def getArguments():
    """Get command line arguments
    """
    parser = ArgumentParser(description = "Edc监控 "\
     " eg: ./monitor.py --tick 3")
     
    parser.add_argument('--tick', dest = 'tick', help = 'timed execution eg. 10')
 
    # Done
    return parser.parse_args()

if __name__ == '__main__':

    args = getArguments()

    tick = args.tick
    if tick:
        tick = int(tick)

    try:

        monitor = EdcMonitor()

        while tick > 0:
            monitor.count+=1
            monitor.run()
            time.sleep(tick)
        else:
            monitor.run()

    except KeyboardInterrupt:

        pass