__author__ = 'hingem'


import sys

from photo_tank.bin.daemon import Daemon
from photo_tank.indexer.watcher import index_watcher
import sched
import time
import logging
import logging.handlers

class MyDaemon(Daemon):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    fh = logging.FileHandler("/tmp/test.log", "w")
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    def run_scheduled(self, message=None):
        index_watcher()

        self.logger.warning("starting indexer...")
        #self.logger.warning('get_file() took {0} seconds; reschedule in {1} seconds'.format(download_time, restart))
        self.scheduler.enter(5, 1, self. run_scheduled)




    def run(self):
        # Build a scheduler object that will look at absolute times
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.logger.warning("Indexer...")
        # start in 1 second
        self.scheduler.enter(1, 1, self.run_scheduled)
        self.scheduler.run()


if __name__ == "__main__":
    daemon = MyDaemon('/tmp/idx.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)

















