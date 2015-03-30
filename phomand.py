__author__ = 'hingem'


#!/usr/bin/env python

import sys, time
from bin.daemon import Daemon

class MyDaemon(Daemon):
    def run(self):
        while True:
            time.sleep(1)

if __name__ == "__main__":
    daemon = MyDaemon('/tmp/phomand.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            Daemon.start()
        elif 'stop' == sys.argv[1]:
            Daemon.stop()
        elif 'restart' == sys.argv[1]:
            Daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)