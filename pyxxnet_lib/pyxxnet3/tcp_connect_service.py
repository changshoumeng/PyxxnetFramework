#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   tcp_connect_service.py
#
#   201706 定义基于epoll的 tcp_connect_service
#
######################################################## #
from . import core_param
from . import core_status
from . import core_utils
from .event_loop import SelectLoop
from .io_handler import *
from .main_loop import ServerInterface

logger = logging.getLogger()
statuslogger = logging.getLogger("statusLogger")
netLogger = logging.getLogger("netLogger")


class TcpConnectEventHandler(object):
    def onTcpEndpointCreate(self, sessionid=0, client_socket=None, connect_addr=(), which=0):
        raise NotImplementedError()

    def onTcpEndpointRelease(self, connection):
        raise NotImplementedError()


class TcpConnectServiceInterface(ServerInterface):
    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def serve_once(self):
        raise NotImplementedError()

    def get_connector(self, fd, sessionid):
        raise NotImplementedError()


'''基于TCP的连接服务，负责主动去连接远程服务器'''
class TcpConnectService(TcpConnectServiceInterface):
    # @listen_addr_list  [(ip,port,which),]
    def __init__(self,
                 connect_addr_list=[],
                 connect_event_loop=SelectLoop(),
                 connect_event_handler=TcpConnectEventHandler()):
        self._connect_addr_list = connect_addr_list
        self._event_loop = connect_event_loop
        self._connect_event_handler = connect_event_handler
        self._is_auto_reconnect = True
        self._is_started = 0
        pass

    # @implement ServerInterface.start()
    def start(self):
        if 1 == self._is_started:
            return True
        self._invalid_connectorfd_set = set()
        self._pending_connector_dict = {}
        self._connector_dict = {}
        self._is_connectable = True
        for i, (ip, port, which) in enumerate(self._connect_addr_list):
            if which < 0:
                continue
            i, addr = i + 1000, (ip, port)
            connector = self._connect_event_handler.onTcpEndpointCreate(i, None, addr, which)
            self._addPendingConnector(connector, delay=0)
        self._is_started = 1
        self._last_timestamp = 0
        netLogger.debug("TcpConnectService.start()")
        return True

    # @implement ServerInterface.stop()
    def stop(self):
        if self._is_started == 0:
            return
        self._is_started = 0
        self._event_loop.close()
        pass

    # @implement ServerInterface.serve_once()
    def serve_once(self):
        # netLogger.debug("TcpConnectService.serve_once1()")
        self._triggerTimerEvent()
        # netLogger.debug("TcpConnectService.serve_once2()")
        rlist, wlist, xlist = self.prepare_elist()
        # print "in:",rlist, wlist, xlist
        readables, writables, exceptionals = self._event_loop.poll(rlist, wlist, xlist, core_param.MAX_EVENT_WAITTIME)
        # print "out:", readables, writables, exceptionals
        for fileno in exceptionals:
            self._onFdExceptional(client_fd=fileno)
        for fileno in readables:
            self._onFdReadable(client_fd=fileno)
        for fileno in writables:
            self._onFdWritable(client_fd=fileno)
        self._checkInvalidFds()
        all = len(readables) + len(writables) + len(exceptionals)
        if all > core_status.max_notify_event_count:
            core_status.max_notify_event_count = all

    def prepare_elist(self):
        rlist, wlist, xlist = [], [], []
        if "select" == self._event_loop.get_loop_type():
            for fileno, connecor in self._connector_dict.items():
                if not connecor:
                    continue
                rlist.append(fileno)
                xlist.append(fileno)
                if connecor.is_register_sendevent():
                    wlist.append(fileno)
        return rlist, wlist, xlist

    '''触发一个定时器事件,完成一些定时JOBS'''
    def _triggerTimerEvent(self):
        n = core_utils.get_timestamp()
        if n > self._last_timestamp + core_param.MAX_TIMEOUT_INTVAL:
            self._last_timestamp = n

            #处理忙连接，让其连接
            for connector in list(self._pending_connector_dict.values()):
                if not connector:
                    continue
                if not connector.can_connect():
                    continue
                self._buildConnection(connector)

            #处理无效连接，让其释放，这里做的是延时释放
            for fileno, connector in self._connector_dict.items():
                connector.on_timer_event()
                if connector.is_loselive():
                    self._invalid_connectorfd_set.add(fileno)

            pass

    def get_connector(self, connector_fd, connector_sessionid):
        connector = self._connector_dict.get(connector_fd, None)
        if not connector:
            netLogger.debug("get_connector() id:<%d,%d>;NULL", connector_fd, connector_sessionid)
            return None
        if connector.client_session_id != connector_sessionid:
            netLogger.debug("get_connector() id:<%d,%d>;not match;realsessionid:%d", connector_fd, connector_sessionid,
                            connector.client_session_id)
            return None
        return connector

    def _onFdReadable(self, client_fd):
        connector = self._connector_dict.get(client_fd, None)
        if connector is None:
            netLogger.critical("read failed,client_fd:%d", client_fd)
            return
        if not connector.on_read_event():
            netLogger.debug("readble;fd:%d on_read_event>false", client_fd)
            self._invalid_connectorfd_set.add(client_fd)

    def _onFdWritable(self, client_fd):
        netLogger.debug("writable;fd:%d", client_fd)
        connector = self._connector_dict.get(client_fd, None)
        if connector is None:
            netLogger.critical("write failed,client_fd:%d", client_fd)
            return
        if connector.is_connecting():
            netLogger.debug("writable;fd:%d is_connecting", client_fd)
            self._delPendingConnector(connector.client_session_id)
            connector.on_connect_event(True)
            return
        if not connector.on_write_event():
            netLogger.debug("writable;fd:%d on_write_event>false", client_fd)
            self._invalid_connectorfd_set.add(client_fd)

    def _onFdExceptional(self, client_fd):
        connector = self._connector_dict.get(client_fd, None)
        if connector is None:
            netLogger.critical("!!!exceptional failed,client_fd:%d", client_fd)
            return
        netLogger.critical("!!!exceptional,client_fd:%d", client_fd)
        self._invalid_connectorfd_set.add(client_fd)
        if connector.is_connecting():
            connector.on_connect_event(False)
        pass

    def _addTcpConnector(self, connector_fd, connector):
        if self._connector_dict.get(connector_fd, None):
            netLogger.warning("addTcpConnector22<%d,%d>conns:%d addr:%s", connector_fd, connector.client_session_id,
                              len(self._connector_dict), str(connector.client_addr))
            return
        self._event_loop.register_io_event(connector_fd)
        self._connector_dict[connector_fd] = connector
        netLogger.debug("addTcpConnector<%d,%d>conns:%d addr:%s", connector_fd, connector.client_session_id,
                        len(self._connector_dict), str(connector.client_addr))

    def _delTcpConnector(self, connector_fd, connector):
        if self._connector_dict.get(connector_fd, None):
            self._event_loop.unregister(connector_fd)
            del self._connector_dict[connector_fd]
            # self._connector_dict[connector_fd]=None
            netLogger.debug("delTcpConnector<%d,%d>conns:%d addr:%s", connector_fd, connector.client_session_id,
                            len(self._connector_dict), str(connector.client_addr))

    def _addPendingConnector(self, connector, delay=0):
        connector_id = connector.client_session_id
        if self._pending_connector_dict.get(connector_id, None):
            netLogger.warning("addPendingConnector22 sessionid:%d", connector_id)
            return
        connector.prepare_next_connect(delay)
        self._pending_connector_dict[connector_id] = connector
        netLogger.debug("addPendingConnector sessionid:%d", connector_id)

    def _delPendingConnector(self, connector_id):
        if self._pending_connector_dict.get(connector_id, None):
            del self._pending_connector_dict[connector_id]
            netLogger.warning("delPendingConnector sessionid:%d", connector_id)
            # self._pending_connector_dict[connector_id] = None

    def _checkInvalidFds(self):
        if not self._invalid_connectorfd_set:
            return
        for client_fd in self._invalid_connectorfd_set:
            connector = self._connector_dict.get(client_fd, None)
            if connector is None:
                continue
            self._delTcpConnector(client_fd, connector)
            if self._is_auto_reconnect:
                self._addPendingConnector(connector, delay=5)
            if not connector.is_connect_failed():
                connector.on_disconnect_event()
            connector.close()
        self._invalid_connectorfd_set.clear()

    '''建立连接，完成三次握手'''
    def _buildConnection(self, connector, is_block_connect=False):
        if not self._is_connectable:
            netLogger.debug("not_connectable")
            connector.prepare_next_connect(5)
            core_utils.wait(5)
            return False

        #这里才赋予了连接器一个连接句柄
        connector.reset_connect_status()
        connect_addr = connector.client_addr
        connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connector.client_socket = connect_socket

        try:
            if not is_block_connect:
                connect_socket.setblocking(False)
                self._addTcpConnector(connect_socket.fileno(), connector)
                connect_socket.connect(connect_addr)
            else:
                connect_socket.connect(connect_addr)
                connect_socket.setblocking(False)
                self._addTcpConnector(connect_socket.fileno(), connector)
            connector.on_connect_event(isOK=True)
            self._delPendingConnector(connector.client_session_id)
            return True
        except socket.error as msg:
            if msg.errno in BUSYING_STATUS:
                netLogger.warning("connecting...<%d,%d> addr:%s", connect_socket.fileno(), connector.client_session_id,
                                  str(connect_addr))
                self._delPendingConnector(connector.client_session_id)
                return True
            else:
                connector.on_connect_event(isOK=False)
                self._is_connectable = False
                netLogger.exception("connect error<%d,%d> addr:%s %s", connect_socket.fileno(),
                                    connector.client_session_id, str(connect_addr), repr(msg))
        return False
