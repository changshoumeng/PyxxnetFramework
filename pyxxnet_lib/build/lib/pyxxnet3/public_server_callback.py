#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   public_server_callback.py
#
#   201710 外部要实现的回调接口，这可理解成一系列的事件，由本网络引擎驱动
#
######################################################## #

class AppWorker(object):
    def __init__(self):
        pass

    '''
    task_on_req
      worker>
          worker.rsp(msg)
      msg>
        msg.msg_id
        msg.msg_mst
        msg.session_uid
        msg.session_data
    '''

    def task_on_req(self, worker, msg):
        pass


class ServerCallback(object):
    worker = AppWorker()
    python="python"

    @staticmethod
    def my_servername():
        return "my_tcp_proxy"

    @staticmethod
    def listenconfig_get(key=""):  # 10.10.2.143
        c = {"addresslist": [("0.0.0.0", 10004, 0)], "eventloop": "select", }
        return c[key]

    @staticmethod
    def connectconfig_get(key=""):
        server_addr_list = [("127.0.0.1", 9414, 0)]
        c = {"addresslist": server_addr_list, "eventloop": "select", }
        # return ""
        return c[key]

    @staticmethod
    def workerconfig_get(key=""):
        c = {"workercount": 0, }
        return c[key]

    @staticmethod
    def server_on_timer():
        pass

    # @return: len(buffer),0  <size,cmd>
    @staticmethod
    def session_unpack_frombuffer(session, buffer):
        # print("session_unpack_frombuffer:",session,buffer)
        buflen = len(buffer)
        return (buflen, 1)

    @staticmethod
    def session_dispatch_packet(session, packet_cmd, packet_data):
        print("session_dispatch_packet() session:{0} cmd:{1} data:{2}".format(session, packet_cmd, packet_data))

    @staticmethod
    def endpoint_unpack_frombuffer(endpoint, buffer):
        buflen = len(buffer)
        return (buflen, 1)

    @staticmethod
    def endpoint_dispatch_packet(endpoint, packet_cmd, packet_data):
        print("endpoint_dispatch_packet() endpoint:{0} cmd:{1} data:{2}".format(endpoint, packet_cmd, packet_data))

    @staticmethod
    def session_keeplive(session, status=0):
        pass

    @staticmethod
    def endpoint_keeplive(endpoint, status=0):
        pass

    @staticmethod
    def task_on_req(worker, msg):
        return

    @staticmethod
    def task_on_rsp(session_uid, session_data):
        cmd, packet_data = session_data
        print("endpoint_dispatch_packet() session_uid:{0} cmd:{1} data:{2}".format(session_uid, cmd, packet_data))
