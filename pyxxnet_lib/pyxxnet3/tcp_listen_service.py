#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   tcp_listen_service.py
#
#   201706 定义基于epoll的 tcpserver
#
######################################################## #

from .event_loop import SelectLoop
from .io_handler import *
from .main_loop import ServerInterface

logger = logging.getLogger()
statuslogger = logging.getLogger("statusLogger")
netLogger = logging.getLogger("netLogger")


class TcpListenEventHandler(object):
    def onTcpSessionCreate(self, sessionid=0, client_socket=None, connect_addr=(), which=0):
        raise NotImplementedError()

    def onTcpSessionRelease(self, connection):
        raise NotImplementedError()


class TcpListenServiceInterface(ServerInterface):
    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def serve_once(self):
        raise NotImplementedError()

    # @acceptor is io_handler
    def get_acceptor(self, sessionid):
        raise NotImplementedError()


class TcpListenService(TcpListenServiceInterface):
    # @listen_addr_list  [(ip,port,which),]
    def __init__(self, listen_addr_list=[], listen_event_loop=SelectLoop(),
                 listen_event_handler=TcpListenEventHandler()):
        self._listen_addr_list = listen_addr_list
        self._event_loop = listen_event_loop
        self._event_handler = listen_event_handler
        self._is_started = 0
        self._listener_dict = {}
        self._acceptor_dict = {}
        pass

    # @implement ServerInterface.start()
    def start(self):
        if 1 == self._is_started:
            return True
        for i, (ip, port, which) in enumerate(self._listen_addr_list):
            if not self._createListenSocket(i, ip, port, which):
                return False
        self._invalid_acceptorfd_set = set()
        self._session_id = 1
        self._is_started = 1
        self._last_timestamp = core_utils.get_timestamp()
        netLogger.debug("start()")
        return True

    # @implement ServerInterface.stop()
    def stop(self):
        if self._is_started == 0:
            return
        self._is_started = 0
        self._event_loop.close()
        for listener in self._listener_dict.values():
            listener.close()
        self._listener_dict.clear()
        for acceptor in self._acceptor_dict.values():
            acceptor.close()
        netLogger.debug("stop()")

    # @implement ServerInterface.serve_once()
    def serve_once(self):
        self._triggerTimerEvent()
        rlist, wlist, xlist = self.prepare_elist()
        readables, writables, exceptionals = self._event_loop.poll(rlist, wlist, xlist, core_param.MAX_EVENT_WAITTIME)

        for fileno in exceptionals:
            self._onFdExceptional(client_fd=fileno)
        for fileno in readables:
            if fileno in self._listener_dict:
                self._onFdAcceptable(listen_fd=fileno)
            else:
                self._onFdReadable(client_fd=fileno)
        for fileno in writables:
            self._onFdWritable(client_fd=fileno)
        self._checkInvalidAcceptors()
        all = len(readables) + len(writables) + len(exceptionals)
        if all > core_status.max_notify_event_count:
            core_status.max_notify_event_count = all

    def get_acceptor(self, sessionid=tuple()):
        acceptor_fd, acceptor_sessionid = sessionid
        if acceptor_fd not in self._acceptor_dict:
            netLogger.debug("get_acceptor NULL;id:<%d,%d>", acceptor_fd, acceptor_sessionid)
            return None
        acceptor = self._acceptor_dict[acceptor_fd]
        if acceptor.client_session_id != acceptor_sessionid:
            netLogger.debug("get_acceptor Failed;id:<%d,%d != %d> ", acceptor_fd, acceptor_sessionid,
                            acceptor.client_session_id)
            return None
        return acceptor

    def prepare_elist(self):
        rlist, wlist, xlist = [], [], []
        if "select" == self._event_loop.get_loop_type():
            for fileno, listener in self._listener_dict.items():
                if not listener:
                    continue
                rlist.append(fileno)
            for fileno, acceptor in self._acceptor_dict.items():
                if not acceptor:
                    continue
                rlist.append(fileno)
                xlist.append(fileno)
                if acceptor.is_register_sendevent():
                    wlist.append(fileno)
        return rlist, wlist, xlist

    def _printstatus(self):
        netLogger.info("<statusinfo> max_doaccept_count:%d max_notify_event_count:%d  fn:%d",core_status.max_doaccept_count,core_status.max_notify_event_count,core_status.max_socket_fileno)
     
    # 定时事件触发器
    def _triggerTimerEvent(self):
        n = core_utils.get_timestamp()
        if n > self._last_timestamp + core_param.MAX_TIMEOUT_INTVAL:
            self._last_timestamp = n
            self._printstatus()
            for fileno, acceptor in self._acceptor_dict.items():
                acceptor.on_timer_event()
                if acceptor.is_loselive():
                    self._invalid_acceptorfd_set.add(fileno)

    def _createListenSocket(self, i, ip, port, which):
        listen_addr = (ip, port)
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            listen_socket.setblocking(0)
            listen_socket.bind(listen_addr)
            listen_socket.listen(core_param.MAX_LISTEN_BACKLOG)
            self._listener_dict[listen_socket.fileno()] = ListenerABC(i, listen_socket, listen_addr, which)
            self._event_loop.register_s_event(listen_socket.fileno())
            netLogger.info("Listen OK;%s", str(listen_addr))
            return True
        except socket.error as  e:
            netLogger.critical("Listen Failed;%s;Error:%s", str(listen_addr), repr(e))
        return False

    def _onFdAcceptable(self, listen_fd):
        listener = self._listener_dict.get(listen_fd, None)
        if not listener:
            netLogger.error("cannot find listener;fd:%d", listen_fd)
            return
        listen_socket = listener.client_socket
        if not listen_socket:
            netLogger.error("cannot find listen_socket;fd:%d", listen_fd)
            return
        accept_count = 0
        
        while True:
            try:
                client_socket, client_address = listen_socket.accept()
                if len(self._acceptor_dict) > core_param.MAX_SESSION_COUNT:
                    netLogger.critical("Accept too Many;Refuse:%s", str(client_address))
                    client_socket.close()
                    return False
                session_id = self._session_id
                self._session_id = session_id + 1
                client_socket.setblocking(0)
                acceptor = self._event_handler.onTcpSessionCreate(session_id, client_socket, client_address,listener.which)
                if session_id%1000==1:
                    netLogger.info("session create:<%d,%d> <%s,%d> conns:%d,", client_socket.fileno(), session_id, str(client_address), listener.which,len(self._acceptor_dict))
                    self._printstatus()
                    
                core_status.max_socket_fileno = max( core_status.max_socket_fileno,  client_socket.fileno() )
                self._addTcpAcceptor(acceptor.client_socket.fileno(), acceptor)
                accept_count += 1
                acceptor.keeplive(LIVE_STATUS.LIVE_STATUS_BEGIN)
            except socket.error as  e:
                if e.errno in BUSYING_STATUS:                     
                    core_status.max_doaccept_count=max(core_status.max_doaccept_count,accept_count )                
                    return True
                else:
                    netLogger.critical("Accept Failed;Error:%s", repr(e))
                return False

    def _onFdReadable(self, client_fd):
        acceptor = self._acceptor_dict.get(client_fd, None)
        if acceptor is None:
            netLogger.critical("read failed,client_fd:%d", client_fd)
            return
        if not acceptor.on_read_event():
            self._invalid_acceptorfd_set.add(client_fd)

    def _onFdWritable(self, client_fd):
        acceptor = self._acceptor_dict.get(client_fd, None)
        if acceptor is None:
            netLogger.critical("write failed,client_fd:%d", client_fd)
            return
        if not acceptor.on_write_event():
            self._invalid_acceptorfd_set.add(client_fd)

    def _onFdExceptional(self, client_fd):
        acceptor = self._acceptor_dict.get(client_fd, None)
        if acceptor is None:
            netLogger.critical("exceptional failed,client_fd:%d", client_fd)
            return
        netLogger.critical("exceptional,client_fd:%d", client_fd)
        self._invalid_acceptorfd_set.add(client_fd)
        pass

    def _checkInvalidAcceptors(self):
        for client_fd in self._invalid_acceptorfd_set:
            acceptor = self._acceptor_dict.get(client_fd, None)
            if acceptor is None:
                continue
            self._delTcpAcceptor(client_fd, acceptor)
            acceptor.on_disconnect_event()
            acceptor.close()
        self._invalid_acceptorfd_set.clear()

    def _addTcpAcceptor(self, acceptor_fd, acceptor):
        self._event_loop.register_io_event(acceptor_fd)
        self._acceptor_dict[acceptor_fd] = acceptor
        #netLogger.debug("addTcpAcceptor<%d,%d>conns:%d addr:%s", acceptor_fd, acceptor.client_session_id, len(self._acceptor_dict), str(acceptor.client_addr))

    def _delTcpAcceptor(self, acceptor_fd, acceptor):
        if acceptor_fd in self._acceptor_dict:
            self._event_loop.unregister(acceptor_fd)
            #netLogger.debug("delTcpAcceptor<%d,%d>conns:%d addr:%s", acceptor_fd, acceptor.client_session_id, len(self._acceptor_dict), str(acceptor.client_addr))
            del self._acceptor_dict[acceptor_fd]
