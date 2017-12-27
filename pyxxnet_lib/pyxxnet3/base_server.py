#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   base_server.py
#
#   201706  本模块实现了一个网络引擎的原型，并组合了直接对外暴露的服务接口public_server_interface，
#   以及本引擎异步事件驱动的事件接口public_server_callback；这将意味着使用本库的人，应该从public_server_interface
#       public_server_callback两个文件着手，而不必关心太多的底层细节。
#
######################################################## #
import logging

managerLogger = logging.getLogger("managerLogger")
logger = logging.getLogger()
from .worker import *
from .tcp_listen_service import TcpListenService
from .tcp_connect_service import TcpConnectService
from .main_loop import *
from .io_handler import *
from .event_loop import *
from . import core_status
from . import pyxxconstant
from .public_server_callback import ServerCallback
from . import core_utils
import os
import sys
import random
import copy
from .message_pipe import FeedbackLikeMessageQueue

if core_utils.is_python3():
    import _thread as thread
else:
    import thread


# In fact,you can treat "PARAM" as a global object
class PARAM:
    appcore_interface = ServerCallback()
    endpoint_dict = {}


class ServerTaskMsgQueue(FeedbackLikeMessageQueue):
    def __init__(self, appcore_interface=ServerCallback()):
        super(ServerTaskMsgQueue, self).__init__()
        self.appcore_interface = appcore_interface

    def rsp(self, m):
        m = copy.deepcopy(m)
        self.push_feedback(m)

    # @ call by worker
    def on_req(self, m):
        rsp_result = self.appcore_interface.task_on_req(self, m)
        if not rsp_result:
            return

        self.push_feedback(rsp_result)

    ##call by master
    def on_rsp(self, m):
        PARAM.appcore_interface.task_on_rsp(m.session_uid, m.session_data)

'''定义一个会话监听器，可以创建会话对象'''
class TcpListenEventHandler(object):
    def onTcpSessionCreate(self, sessionid=0, client_socket=None, connect_addr=(), which=0):
        return Session(sessionid, client_socket, connect_addr, which)

    def onTcpSessionRelease(self, connection):
        pass
        # raise NotImplementedError()

'''定义一个会话，包装连接过来的客户'''
class Session(SessionABC):
    def unpack_frombuffer(self, buffer):
        return PARAM.appcore_interface.session_unpack_frombuffer(self, buffer)

    def dispatch_packet(self, packet_cmd, packet_data):
        core_status.runingdata.recv( len(packet_data))
        return PARAM.appcore_interface.session_dispatch_packet(self, packet_cmd, packet_data)

    def send(self, data):
        core_status.runingdata.send( len(data))
        return  super(Session, self).send(data)

    def keeplive(self, keepstatus=LIVE_STATUS.LIVE_STATUS_END):
        return PARAM.appcore_interface.session_keeplive(self, keepstatus)

    def __str__(self):
        return "Session(id:{0} fd:{1} which:{2})".format(self.client_session_id, self.client_socket.fileno(),
                                                         self.which)

'''定义一个构造终端的事件句柄'''
class TcpConnectEventHandler(object):
    def onTcpEndpointCreate(self, sessionid=0, client_socket=None, connect_addr=(), which=0):
        ep = Endpoint(sessionid, client_socket, connect_addr, which)
        if which not in PARAM.endpoint_dict:
            PARAM.endpoint_dict[which] = [ep]
        else:
            PARAM.endpoint_dict[which].append(ep)
        return ep

    def onTcpSessionRelease(self, connection):
        pass
        # print "connection release"


'''定义一个终端'''
class Endpoint(EndpointABC):
    # @client_session_id int,invalid if client_session_id<=0
    # @connect_socket socket object
    # @server_addr  (ip,port)
    # @which int,server type
    def __init__(self, client_session_id=-1, connect_socket=None, server_addr=(), which=0):
        super(Endpoint, self).__init__(client_session_id, connect_socket, server_addr, which)
        self.connection_type = CONNECT_TYPE.IS_CONNECTOR
        self.connect_status = CONNECT_STATUS.CONNECT_CLOSED

    def on_connect_event(self, isOK=True):
        super(Endpoint, self).on_connect_event(isOK)

    def unpack_frombuffer(self, buffer):
        return PARAM.appcore_interface.endpoint_unpack_frombuffer(self, buffer)

    def dispatch_packet(self, packet_cmd, packet_data):
        return PARAM.appcore_interface.endpoint_dispatch_packet(self, packet_cmd, packet_data)

    def keeplive(self, keepstatus=LIVE_STATUS.LIVE_STATUS_END):
        return PARAM.appcore_interface.endpoint_keeplive(self, keepstatus)




class WorkerHandler(object):
    def __init__(self, workerid=0, message_queue=None):
        self.workerid = workerid
        self.message_queue = message_queue

    def start(self):
        self.pid = os.getpid()
        managerLogger.debug("worker(%d) start in pid(%d)", self.workerid, self.pid)
        with open("run/worker_{0}.pid".format(self.workerid), "w") as f:
            f.write(str(self.pid))
            f.write(" ")
        return True

    def stop(self):
        self.pid = os.getpid()
        managerLogger.debug("worker(%d) stop in pid(%d)", self.workerid, self.pid)

    def serve_once(self):
        self.message_queue.pop_task()
        # return appcore_interface.worker_serve_once(self)

    def is_stop(self):
        return graceful_event.is_stop()


def _manager_thread_handler(message_queue):
    managerLogger.debug("_manager_thread start")
    try:
        while not graceful_event.is_stop():
            message_queue.pop_feedback()
        else:
            managerLogger.error("_manager_thread got parent exit notify")
            return
    except GracefulExitException:
        managerLogger.error("_manager_thread got graceful exit exception.")
        return
    except:
        info = sys.exc_info()
        t = '**************_manager_thread caught exception*************'
        for f, l, func, text in traceback.extract_tb(info[2]):
            t += "\n[file]:{0} [{1}] [{2}] {3}".format(f, l, func, text)
        t += "\n[info]:%s->%s\n" % info[:2]
        managerLogger.exception(t)
    finally:
        managerLogger.critical("_manager_thread exit")


# _server_taskqueue=None


class BaseServer(ServerInterface):
    def __init__(self):
        self.workers = []
        self.pid = os.getpid()
        self.listenservice = None
        self.connectservice = None
        self.message_queue = None
        self.last_timestamp = core_utils.get_timestamp()

    def start(self):
        managerLogger.debug("BaseServer.main start at pid:%d", self.pid)
        if not self.start_tcplistenservice():
            return False
        if not self.start_tcpconnectservice():
            return False
        if not self.start_worker():
            return False
        with open("run/master.pid", "w") as f:
            f.write(str(self.pid))
            f.write(" ")
        return True

    def stop(self):
        managerLogger.info("=============main stop==============")
        graceful_event.notify_stop()
        if self.listenservice:
            self.listenservice.stop()
        if self.connectservice:
            self.connectservice.stop()
        core_utils.wait(2)
        for worker in self.workers:
            worker.stop()
        managerLogger.info("=============main stop end==============")

    def serve_once(self):
        if self.listenservice:
            self.listenservice.serve_once()
        if self.connectservice:
            self.connectservice.serve_once()
        if core_utils.get_timestamp() > self.last_timestamp + 10:
            PARAM.appcore_interface.server_on_timer()
            core_status.runingdata.report()
            self.last_timestamp = core_utils.get_timestamp()

    def is_stop(self):

        if not self.workers:
            return False
        try:
            for worker in self.workers:
                # print "main process({0}) observe child status=>name:{1} pid:{2} is_alive:{3}".format(os.getpid(), wp.name,wp.pid,wp.is_alive(),)
                if worker.is_alive():
                    return False
        except GracefulExitException:
            self.notify_stop()
            managerLogger.error("master process(%d) got graceful exit exception.", self.pid)
        except:
            self.notify_stop()
            info = sys.exc_info()
            t = '**************main(%d) caught exception*************' % (self.pid)
            for f, l, func, text in traceback.extract_tb(info[2]):
                t += "\n[file]:{0} [{1}] [{2}] {3}".format(f, l, func, text)
            t += "\n[info]:%s->%s\n" % info[:2]
            managerLogger.exception(t)
        return True

    def start_tcplistenservice(self):
        addresslist = PARAM.appcore_interface.listenconfig_get("addresslist")
        if not addresslist:
            managerLogger.debug("tcplistenservice addresslist is NULL")
            return True
        eventloop = PARAM.appcore_interface.listenconfig_get("eventloop")
        el = SelectLoop() if eventloop == "select" else EpollLoop()
        eh = TcpListenEventHandler()
        self.listenservice = TcpListenService(addresslist, el, eh)
        return self.listenservice.start()

    def start_tcpconnectservice(self):
        addresslist = PARAM.appcore_interface.connectconfig_get("addresslist")
        if not addresslist:
            managerLogger.debug("tcpconnectservice addresslist is NULL")
            return True
        eventloop = PARAM.appcore_interface.connectconfig_get("eventloop")
        managerLogger.debug("start_tcpconnectservice;eventloop:%s;addresslist:%s", eventloop, str(addresslist))
        el = SelectLoop() if eventloop == "select" else EpollLoop()
        eh = TcpConnectEventHandler()
        self.connectservice = TcpConnectService(addresslist, el, eh)
        return self.connectservice.start()

    def start_worker(self):
        workercount = PARAM.appcore_interface.workerconfig_get("workercount")
        if 0 == workercount:
            return True
        self.workers = []
        self._server_taskqueue = ServerTaskMsgQueue(PARAM.appcore_interface.worker)
        for i in range(workercount):
            wp = Worker(worker_name="worker_{0}".format(i), interface=WorkerHandler(i, self._server_taskqueue))
            wp.start()
            self.workers.append(wp)
        thread.start_new_thread(_manager_thread_handler, (self._server_taskqueue,))
        return True

    def send_to_session(self, sessionid, data):
        session = self.listenservice.get_acceptor(sessionid)
        if not session:
            logger.warning("send_to_session;cannot find session<%s>", str(sessionid))
            return False
        # logger.debug("send_to_session;sessionid<%s> data:%s", str(sessionid), data)
        return session.send(data)

    def send_to_endpoint(self, which, data):
        ep_list = PARAM.endpoint_dict.get(which, None)
        if not ep_list:
            logger.warning("send_to_endpoint;cannot find which<%s>", str(which))
            return False
        ep = random.choice(ep_list)
        # logger.debug("send_to_endpoint;which<%s> data:%s", str(which), data)

        return ep.send(data)

    def send_to_taskQ(self, m):
        self._server_taskqueue.push_task(m)

    def send_to_feedbackQ(self, m):
        self._server_taskqueue.push_feedback(m)
