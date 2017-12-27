# !/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   io_handler.py
#
#   201706 定义TcpIoHandlerInterface
# 类的关系：
# TcpIoHandlerInterface <---实现---- TcpIoHandler
#                                       |------继承-----  ListenerABC
#                                       |------继承-----  SessionABC
#                                       |------继承-----  EndpointABC
# 注意：keeplive 表征这一个连接的生命周期，通过LIVE_STATUS，这超级有趣。
######################################################## #
import errno
import logging
import socket
import sys
import threading
import traceback

from . import core_param
from . import core_status
from . import core_utils
from .pyxxconstant import *

logger = logging.getLogger()
statuslogger = logging.getLogger("statusLogger")
netLogger = logging.getLogger("netLogger")
BUSYING_STATUS = {errno.EAGAIN, errno.EWOULDBLOCK, errno.EINPROGRESS, errno.EINTR}


# TCP 网络IO事件接口，定义了一个socket句柄上的关联的事件列表
############################################################################
class TcpIoHandlerInterface(object):
    def close(self):
        raise NotImplementedError()

    def get_session_uid(self):
        raise NotImplementedError()

    def send(self, data):
        raise NotImplementedError()

    def keeplive(self, keepstatus=LIVE_STATUS.LIVE_STATUS_END):
        raise NotImplementedError()

    def is_connected(self):
        raise NotImplementedError()

    def is_loselive(self):
        raise NotImplementedError()

    def is_register_sendevent(self):
        raise NotImplementedError()

    def on_read_event(self):
        raise NotImplementedError()

    def on_write_event(self):
        raise NotImplementedError()

    def on_disconnect_event(self):
        raise NotImplementedError()

    def on_timer_event(self):
        raise NotImplementedError()


# 基于TcpIoHandlerInterface接口，做的一个基本功能的实现
############################################################################
class TcpIoHandler(TcpIoHandlerInterface):
    '''
       连接器的基类
    '''
    __slots__ = (
        'connection_type', 'client_session_id', 'client_socket', 'client_addr', 'connect_status', 'recv_buffer',
        'send_buffer', 'send_buffer_lock', 'send_bytes', 'recv_bytes', 'last_recv_time', 'which',)

    def __init__(self, client_session_id=-1, client_socket=None, client_addr=(), which=0):
        self.connection_type = CONNECT_TYPE.IS_ACCEPTOR
        self.client_session_id = client_session_id
        self.client_socket = client_socket
        self.client_addr = client_addr
        self.connect_status = CONNECT_STATUS.CONNECT_SUCC
        self.recv_buffer = core_param.NULL_BYTE
        self.send_buffer = core_param.NULL_BYTE
        self.send_buffer_lock = threading.Lock()
        self.last_recv_time = core_utils.get_timestamp()
        self.send_bytes = 0
        self.recv_bytes = 0
        self.which = which


    def __str__(self):
        sessionid=self.get_session_uid() if self.client_socket else (0,0)
        if self.connection_type == CONNECT_TYPE.IS_ACCEPTOR:
            s = 'Acceptor<sid:{0} addr:{1} stat:{2} which:{3}>'.format(
                sessionid,
                self.client_addr,
                self.connect_status,
                self.which)
        else:
            s = 'Connector<sid:{0} addr:{1} stat:{2} which:{3}>'.format(
                sessionid,
                self.client_addr,
                self.connect_status,
                self.which)
        return s

    def close(self):
        netLogger.warning("session(%d) close;status:%d", self.client_session_id, self.connect_status)
        if self.client_socket:
            self.client_socket.close()
        self.connect_status = CONNECT_STATUS.CONNECT_CLOSED
        self.send_buffer = core_param.NULL_BYTE
        self.recv_buffer = core_param.NULL_BYTE
        self.send_bytes = 0
        self.recv_bytes = 0
        self.client_socket = None

    def on_read_event(self):
        recv_count = 0
        while self.connect_status == CONNECT_STATUS.CONNECT_SUCC:
            self.last_recv_time = core_utils.get_timestamp()
            try:
                if recv_count > core_param.MAX_RECV_COUNT:
                    netLogger.warning("session(%d) recv too slow", self.client_session_id)
                    return True
                canrecvLen = core_param.MAX_RECV_BUFFER_SIZE - len(self.recv_buffer)
                if canrecvLen <= 4:
                    self.connect_status = CONNECT_STATUS.CONNECT_SYS_WILLCLOSED
                    netLogger.warning("session(%d) recv buffer is full", self.client_session_id)
                    return False
                data = self.client_socket.recv(canrecvLen)
                if not data:
                    netLogger.warning("session(%d) recv 0 byte", self.client_session_id)
                    self.connect_status = CONNECT_STATUS.CONNECT_CLI_WILLCLOSED
                    return False
                recvonce_size = len(data)
                core_status.max_recvonce_size = recvonce_size if recvonce_size > core_status.max_recvonce_size else core_status.max_recvonce_size
                self.recv_bytes += recvonce_size
                recv_count += 1
                # print(type(self.recv_buffer),type(data) )
                self.recv_buffer += data
                processed_size = self.__on_process_recvbuffer_event()
                if processed_size == len(self.recv_buffer):
                    self.recv_buffer = core_param.NULL_BYTE
                elif processed_size < len(self.recv_buffer):
                    self.recv_buffer = self.recv_buffer[processed_size:]
                elif processed_size == 0:
                    pass
                else:
                    self.connect_status = CONNECT_STATUS.CONNECT_SER_WILLCLOSED
                    return False
            except socket.error as  msg:
                if msg.errno in BUSYING_STATUS:
                    return True
                else:
                    netLogger.warning("session(%d) recv error:%s", self.client_session_id, repr(msg))
                    self.connect_status = CONNECT_STATUS.CONNECT_SYS_WILLCLOSED
                    return False
            except:
                self.connect_status = CONNECT_STATUS.CONNECT_SYS_WILLCLOSED
                netLogger.warning("session(%d) recv exception", self.client_session_id)
                info = sys.exc_info()
                t = '**************caught exception*************'
                for f, l, func, text in traceback.extract_tb(info[2]):
                    t += "\n[file]:{0} [{1}] [{2}] {3}".format(f, l, func, text)
                t += "\n[info]:%s->%s\n" % info[:2]
                netLogger.exception(t)
                return False
        return False

    # 有两种情况触发onWriteEvent事件
    # 1.epoll通知
    # 2.用户send时且is_writtable=True，可能直接触发
    def on_write_event(self):
        if len(self.send_buffer) == 0:
            return True
        sendLen = 0
        while self.connect_status == CONNECT_STATUS.CONNECT_SUCC:
            with self.send_buffer_lock:
                try:
                    willsendLen = len(self.send_buffer) - sendLen
                    if willsendLen == 0:
                        self.send_buffer = core_param.NULL_BYTE
                        return True
                    sendonce_size = self.client_socket.send(self.send_buffer[sendLen:])
                    core_status.max_sendonce_size = sendonce_size if sendonce_size > core_status.max_sendonce_size else core_status.max_sendonce_size
                    sendLen += sendonce_size
                    self.send_bytes += sendonce_size
                    # 在全部发送完毕后退出 while 循环
                    if sendLen == len(self.send_buffer):
                        # netLogger.debug("finish send:%s", len(self.send_buffer) )
                        self.send_buffer = core_param.NULL_BYTE
                        return True
                    else:
                        netLogger.warning("please continue to send; sendLen:%d totalLen:%d", sendLen,
                                          len(self.send_buffer))
                except socket.error as  msg:
                    if msg.errno in BUSYING_STATUS:
                        netLogger.warning("please send after while; sendLen:%d totalLen:%d", sendLen,
                                          len(self.send_buffer))
                        self.send_buffer = self.send_buffer[sendLen:]
                        return True
                    else:
                        netLogger.warning("session(%d) send error:%s", self.client_session_id, repr(msg))
                        self.connect_status = CONNECT_STATUS.CONNECT_SYS_WILLCLOSED
                        return False
                except:
                    self.connect_status = CONNECT_STATUS.CONNECT_SYS_WILLCLOSED
                    info = sys.exc_info()
                    t = '**************caught exception*************'
                    for f, l, func, text in traceback.extract_tb(info[2]):
                        t += "\n[file]:{0} [{1}] [{2}] {3}".format(f, l, func, text)
                    t += "\n[info]:%s->%s\n" % info[:2]
                    netLogger.exception(t)
        return True

    # 这里可以加锁，以适应多线程的send安全性；这里简单实现sendData过程
    # 这里可以做很大的优化
    def send(self, data):
        if self.connect_status != CONNECT_STATUS.CONNECT_SUCC:
            netLogger.warning("session(%d) send error,status:%d,invalid connection", self.client_session_id,
                              self.connect_status)
            return False
        with self.send_buffer_lock:
            if len(self.send_buffer) > core_param.MAX_SEND_BUFFER_SIZE:
                netLogger.warning("session(%d) send error,send buffer full", self.client_session_id)
                return False
            self.send_buffer += data
        self.on_write_event()
        return True

    def on_disconnect_event(self):
        if self.connect_status == CONNECT_STATUS.CONNECT_CLOSED:
            return
        netLogger.warning("session(%d) on_disconnect_event", self.client_session_id)
        self.connect_status = CONNECT_STATUS.CONNECT_CLOSED
        self.keeplive(LIVE_STATUS.LIVE_STATUS_END)
        # special cmd is -1

    def on_timer_event(self):
        if self.connect_status == CONNECT_STATUS.CONNECT_SUCC:
            if CONNECT_TYPE.IS_ACCEPTOR == self.connection_type:
                if core_utils.get_timestamp() > self.last_recv_time + core_param.MAX_KEEPLIVE_TIME * 2:
                    idle = core_utils.get_timestamp() - self.last_recv_time
                    netLogger.warning("session(%d) on_timer,loselive;idletime:%d", self.client_session_id, idle)
                    self.connect_status = CONNECT_STATUS.CONNECT_LOSELIVE
            else:
                if core_utils.get_timestamp() > self.last_recv_time + core_param.MAX_KEEPLIVE_TIME:
                    idle = core_utils.get_timestamp() - self.last_recv_time
                    netLogger.warning("session(%d) on_timer,loselive;idletime:%d", self.client_session_id, idle)
                    self.connect_status = CONNECT_STATUS.CONNECT_LOSELIVE
                else:
                    self.keeplive(LIVE_STATUS.LIVE_STATUS_KEEPLIVE)

        pass

    # 处理收到的数据
    def __on_process_recvbuffer_event(self):
        total_bufsize = len(self.recv_buffer)
        has_unpack_bufsize = 0
        while has_unpack_bufsize < total_bufsize:
            unpack_size, cmd = self.unpack_frombuffer(self.recv_buffer[has_unpack_bufsize:])
            if unpack_size == 0:
                break
            if unpack_size < 0:
                netLogger.error("__on_process_recvbuffer_event;unpack error:%d", unpack_size)
                return unpack_size
            self.dispatch_packet(cmd, self.recv_buffer[has_unpack_bufsize:has_unpack_bufsize + unpack_size])
            has_unpack_bufsize += unpack_size
        return has_unpack_bufsize

    def is_connected(self):
        return self.connect_status == CONNECT_STATUS.CONNECT_SUCC

    def is_loselive(self):
        return self.connect_status == CONNECT_STATUS.CONNECT_LOSELIVE

    def is_register_sendevent(self):
        if len(self.send_buffer) > 0:
            return True
        if not self.is_connected():
            return True
        return False

    def keeplive(self, keepstatus=LIVE_STATUS.LIVE_STATUS_END):
        pass

    def get_session_uid(self):
        return (self.client_socket.fileno(), self.client_session_id)

    # @result (size,cmd)
    def unpack_frombuffer(self, buffer):
        raise NotImplementedError()

    def dispatch_packet(self, packet_cmd, packet_data):
        raise NotImplementedError()


# 基于TcpIoHandler父类，抽取出适合于Listener的接口，这类排除了unpack_frombuffer，dispatch_packet
############################################################################
class ListenerABC(TcpIoHandler):
    def __init__(self, client_session_id=-1, client_socket=None, client_addr=(), which=0):
        super(ListenerABC, self).__init__(client_session_id, client_socket, client_addr, which)
        self.connection_type = CONNECT_TYPE.IS_LISTENTOR
        self.connect_status = CONNECT_STATUS.CONNECT_SUCC

    def unpack_frombuffer(self, buffer):
        return 0, len(buffer)

    def dispatch_packet(self, packet_cmd, packet_data):
        pass


# 基于TcpIoHandler父类，抽取出适合于Session的接口，主要是换了一个贴切的名字，叫做Session
############################################################################
class SessionABC(TcpIoHandler):
    def __init__(self, client_session_id=-1, client_socket=None, client_addr=(), which=0):
        super(SessionABC, self).__init__(client_session_id, client_socket, client_addr, which)
        self.connection_type = CONNECT_TYPE.IS_ACCEPTOR
        self.connect_status = CONNECT_STATUS.CONNECT_SUCC

    def unpack_frombuffer(self, buffer):
        return 0, len(buffer)

    def dispatch_packet(self, packet_cmd, packet_data):
        pass

    def keeplive(self, keepstatus=LIVE_STATUS.LIVE_STATUS_END):
        pass


# 基于TcpIoHandler父类，抽取出适合于Session的接口，主要是换了一个贴切的名字，叫做Endpoint
############################################################################
class EndpointABC(TcpIoHandler):
    def __init__(self, client_session_id=-1, connect_socket=None, server_addr=(), which=0):
        super(EndpointABC, self).__init__(client_session_id, connect_socket, server_addr, which)
        self.connection_type = CONNECT_TYPE.IS_CONNECTOR
        self.connect_status = CONNECT_STATUS.CONNECT_CLI_WILLCONNECT
        self.next_connect_time = core_utils.get_timestamp()

    def prepare_next_connect(self, delay=0):
        self.next_connect_time = core_utils.get_timestamp() + delay
        netLogger.debug("prepare_next_connect() delay:%d", delay)

    def can_connect(self):
        if self.is_connected():
            return False
        # if self.is_connecting():
        #     return False
        if self.connect_status == CONNECT_STATUS.CONNECT_CLI_WILLCONNECT:
            return True
        if core_utils.get_timestamp() >= self.next_connect_time:
            return True
        return False

    # 重置连接状态
    def reset_connect_status(self):
        self.connect_status = CONNECT_STATUS.CONNECT_DOING
        self.next_connect_time = core_utils.get_timestamp()
        self.keeplive(LIVE_STATUS.LIVE_STATUS_REPAIR)
        pass

    def on_connect_event(self, isOK=True):
        self.connect_status = CONNECT_STATUS.CONNECT_SUCC if isOK else CONNECT_STATUS.CONNECT_FAIL
        if isOK:
            self.keeplive(LIVE_STATUS.LIVE_STATUS_BEGIN)
        else:
            self.keeplive(LIVE_STATUS.LIVE_STATUS_END)
        netLogger.debug("on_connect_event() %s ", self)
        pass

    def is_connecting(self):
        return self.connect_status == CONNECT_STATUS.CONNECT_DOING

    def is_connect_failed(self):
        return self.connect_status == CONNECT_STATUS.CONNECT_FAIL

    def unpack_frombuffer(self, buffer):
        return 0, len(buffer)

    def dispatch_packet(self, packet_cmd, packet_data):
        pass

    def keeplive(self, keepstatus=LIVE_STATUS.LIVE_STATUS_END):
        pass
