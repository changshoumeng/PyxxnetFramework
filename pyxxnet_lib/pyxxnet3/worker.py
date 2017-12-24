# -*- coding: utf-8 -*-
# !/usr/bin/env python
#   process_pool.py

#
# refer:
#   http://stackoverflow.com/questions/26414704/how-does-a-python-process-exit-gracefully-after-receiving-sigterm-while-waiting?rq=1
#   http://www.cnblogs.com/kaituorensheng/p/4445418.html
# init created: 2016-07-13
# last updated: 2016-07-14
#
#######################################################################
import multiprocessing
import os

from .main_loop import *

managerLogger = logging.getLogger("managerLogger")


class GracefulExitException(Exception):
    @staticmethod
    def sigterm_handler(signum, frame):
        raise GracefulExitException()

    pass


class GracefulExitEvent(object):
    def __init__(self):
        self.exit_event = multiprocessing.Event()
        signal.signal(signal.SIGTERM, GracefulExitException.sigterm_handler)
        pass

    def is_stop(self):
        return self.exit_event.is_set()

    def notify_stop(self):
        self.exit_event.set()


graceful_event = GracefulExitEvent()


def worker_process_handler(interface):
    pid = os.getpid()
    if interface.start():
        managerLogger.info("worker(%d) start ok", pid)
    else:
        managerLogger.error("worker(%d) start failed", pid)
        return
    try:
        while not interface.is_stop():
            interface.serve_once()
            # core_utils.wait(3)
        else:
            managerLogger.error("worker(%d) got parent exit notify", pid)
            return
    except GracefulExitException:
        managerLogger.error("worker(%d) got graceful exit exception", pid)
        return
    except:
        info = sys.exc_info()
        t = '**************worker(%d) caught exception*************' % (pid)
        for f, l, func, text in traceback.extract_tb(info[2]):
            t += "\n[file]:{0} [{1}] [{2}] {3}".format(f, l, func, text)
        t += "\n[info]:%s->%s\n" % info[:2]
        managerLogger.exception(t)
        return
    finally:
        interface.stop()


class Worker(object):
    # ServerInterface.start()
    def __init__(self, worker_name="worker", interface=ServerInterface()):
        self.worker_name = worker_name
        self.interface = interface
        self.wp = None

    def start(self):
        self.wp = multiprocessing.Process(name=self.worker_name, target=worker_process_handler, args=(self.interface,))
        # self.wp.is_alive()
        self.wp.daemon = False
        self.wp.start()
        return True

    # ServerInterface.stop()
    def stop(self):
        if self.wp:
            pass
            self.wp.terminate()

    def is_alive(self):
        return self.wp.is_alive()
