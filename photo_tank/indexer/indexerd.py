__author__ = 'hingem'


import sys

from photo_tank.bin.daemon import Daemon
from photo_tank.indexer.index_files import index_watcher, set_keywords
from photo_tank.indexer.index_locations import location_watcher
from photo_tank.indexer.index_to_dropbox import update_to_dropbox
from photo_tank.app import app
from time import sleep
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


    def run_watcher(self):
        app.logger.debug("starting new watcher cycle")
        # self.logger.warning("starting keyword indexer..." + str(time.time()))
        # set_keywords()
        # self.logger.warning("starting file indexer..." + str(time.time()))
        # index_watcher()
        # self.logger.warning("starting location indexer..." + str(time.time()))
        location_watcher()






    def run(self):

        while True:
            app.logger.debug("starting new watcher cycle")

            if app.config["WATCHER_FILES"]:
                app.logger.debug("Running file whatcher")
                index_watcher()

            if app.config["WATCHER_LOCATION"]:
                app.logger.debug("Running location whatcher")
                location_watcher()

            if app.config["WATCHER_DROPBOX"]:
                app.logger.debug("Running Dropbox whatcher")
                update_to_dropbox()

            sleep(app.config["WATCHER_INTEVAL"])


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

















