#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   event_loop.py
#
#   201706 定义常见的事件循环
#
######################################################## #

import errno
import logging
import select

netLogger = logging.getLogger("netLogger")

BUSYING_STATUS = {errno.EAGAIN, errno.EWOULDBLOCK, errno.EINPROGRESS, errno.EINTR}


class EventLoop(object):
    def __init__(self, ):
        self._loop_type = ""

    def get_loop_type(self):
        return self._loop_type

    def close(self):
        pass

    def register_s_event(self, fd):
        pass

    def register_io_event(self, fd):
        pass

    # def unregister(self, fd):
    #     pass

    def modify(self, fd, event_type):
        pass

    def poll(self, rlist=[], wlist=[], xlist=[], timeout=0.1):
        readables, writables, exceptionals = [], [], []
        return readables, writables, exceptionals


class EpollLoop(object):
    def __init__(self, ):
        if not hasattr(select, 'epoll'):
            raise SystemError("Not support epoll for current system.")
        self._epoll = select.epoll()
        self._loop_type = "epoll"

    def get_loop_type(self):
        return self._loop_type;

    def close(self):
        self._epoll.close()

    # def register(self, fd, event_type):
    #     self._epoll.register(fd, event_type)

    def register_s_event(self, fd):
        self._epoll.register(fd, select.EPOLLIN)

    def register_io_event(self, fd):
        self._epoll.register(fd, select.EPOLLET | select.EPOLLOUT | select.EPOLLIN)

    def unregister(self, fd):
        self._epoll.unregister(fd)

    def modify(self, fd, event_type):
        self._epoll.modify(fd, event_type)
        print("epoll loop modify fd:{0} event:{1}".format(fd, event_type))

    def poll(self, rlist=[], wlist=[], xlist=[], timeout=0.1):
        readables, writables, exceptionals = [], [], []
        try:
            epoll_list = self._epoll.poll(timeout)
            for fileno, events in epoll_list:
                if events & (select.EPOLLHUP | select.EPOLLERR):
                    exceptionals.append(fileno)
                elif events & select.EPOLLIN:
                    readables.append(fileno)
                elif events & select.EPOLLPRI:
                    readables.append(fileno)
                elif events & select.EPOLLOUT:
                    writables.append(fileno)
        except select.error as msg:
            if msg[0] == 4:
                pass
                # netLogger.debug("poll is busying")
            else:
                netLogger.critical("poll error;error:%s", str(msg))

        return readables, writables, exceptionals


class SelectLoop(object):
    def __init__(self, ):
        self._loop_type = "select"

    def get_loop_type(self):
        return self._loop_type;

    def close(self):
        pass

    def register_s_event(self, fd):
        pass

    def register_io_event(self, fd):
        pass

    def unregister(self, fd):
        pass

    def modify(self, fd, event_type):
        pass

    def poll(self, rlist=[], wlist=[], xlist=[], timeout=0.1):
        if not (rlist or wlist or xlist):
            return [], [], []
        try:
            return select.select(rlist, wlist, xlist, timeout)
        except select.error as  msg:
            if msg[0] == 4:
                pass
                # netLogger.debug("poll is busying")
            else:
                # event_loop 132 poll error;error:(9, 'Bad file descriptor')
                netLogger.critical("poll error;error:%s", str(msg))

        return [], [], []
