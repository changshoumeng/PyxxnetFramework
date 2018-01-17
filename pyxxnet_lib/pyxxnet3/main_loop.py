#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   server_interface.py
#
#   201706 定义服务接口与主循环
#
######################################################## #


import logging
import signal
import sys
import threading
import traceback

netLogger = logging.getLogger("netLogger")
managerLogger = logging.getLogger("managerLogger")

_is_sigint_up = False
_is_continue_event = threading.Event()


def sigint_handler(signum, frame):
    global _is_sigint_up
    global _is_continue_event
    _is_sigint_up = True
    _is_continue_event.set()
    managerLogger.exception("caught interrupt signal:%d", signum)


class ServerInterface(object):
    '''
    class ServerInterface
     定义一个Server的通用接口，被InterruptableTaskLoop调用

    '''

    # ServerInterface.start()
    def start(self):
        raise NotImplementedError()

    # ServerInterface.stop()
    def stop(self):
        raise NotImplementedError()

    # ServerInterface.serve_once()
    def serve_once(self):
        raise NotImplementedError()

    def is_stop(self):
        return False


class InterruptableTaskLoop(object):
    '''
        class InterruptableTaskLoop
        定义可信号中断的事件循环
    '''

    def __init__(self, worker=ServerInterface(), timeout=0):
        if not hasattr(worker, 'start'):
            raise AttributeError("AttributeError:miss method called start() ")
        if not hasattr(worker, 'serve_once'):
            raise AttributeError("AttributeError:miss method called serve_once() ")
        if not hasattr(worker, 'stop'):
            raise AttributeError("AttributeError:miss method called stop() ")
        self.worker = worker
        self.timeout = timeout
        pass

    @staticmethod
    def wait(timeout):
        global _is_continue_event
        if int(timeout) == 0:
            return
        try:
            _is_continue_event.clear()
            _is_continue_event.wait(timeout=timeout)
        except Exception as  e:
            # print "except",e
            pass

    # wait for a while
    def _wait(self):
        if self.timeout != 0:
            InterruptableTaskLoop.wait(self.timeout)

    def _tryonce(self):
        try:
            self.worker.serve_once()
        except:
            info = sys.exc_info()
            t = '**************caught exception*************'
            for f, l, func, text in traceback.extract_tb(info[2]):
                t += "\n[file]:{0} [{1}] [{2}] {3}".format(f, l, func, text)
            t += "\n[info]:%s->%s\n" % info[:2]
            managerLogger.exception(t)
            sys.exit(0)

    # if start succ then run a eventloop
    def startAsForver(self):
        global _is_sigint_up
        global _is_continue_event
        _is_sigint_up = False
        if not self.worker.start():
            managerLogger.critical("worker.start() failed")
            return
        self._tryonce()
        signal.signal(signal.SIGINT, sigint_handler)
        while True:
            try:
                if _is_sigint_up:
                    break

                if self.worker.is_stop():
                    managerLogger.debug("self.worker.is_stop() True")
                    break
                self._wait()
                self.worker.serve_once()
            except:
                info = sys.exc_info()
                t = '**************main loop>caught exception*************'
                for f, l, func, text in traceback.extract_tb(info[2]):
                    t += "\n[file]:{0} [{1}] [{2}] {3}".format(f, l, func, text)
                t += "\n[info]:%s->%s\n" % info[:2]
                managerLogger.exception(t)
        else:
            managerLogger.critical("normal exit")
        self.worker.stop()
