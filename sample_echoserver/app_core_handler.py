#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   netcore_interface.py
#
#   20171017
#
######################################################## #
import logging
logger = logging.getLogger()

from pyxxnet3 import public_server_callback
from pyxxnet3 import public_server_interface
import process_packet,app_worker,param



class APP_CORE_HANDLER(public_server_callback.ServerCallback):
    endpoint_ids = [i for i in range(1)]
    endpoint_session_map = {}
    session_endpoint_map = {}
    worker = app_worker.AppWorker()
    python = "python27"

    def __init__(self):
        pass

    @staticmethod
    def my_servername():
        return param.service_name

    @staticmethod
    def listenconfig_get(key=""):  # 10.10.2.143
        c = {"addresslist": [("0.0.0.0", 8303, 0)], "eventloop": "epoll", }
        for i in range(1000):
            addr=("0.0.0.0", 9000+i, i)
            c["addresslist"].append(addr )
        return c[key]

    @staticmethod
    def connectconfig_get(key=""):
        server_addr_list = [("127.0.0.1", 9414, i) for i in APP_CORE_HANDLER.endpoint_ids]
        c = {"addresslist": server_addr_list, "eventloop": "select", }
        return ""

    @staticmethod
    def workerconfig_get(key=""):
        c = {"workercount": 0, }
        return c[key]

    # @return: len(buffer),0  <size,cmd>
    @staticmethod
    def session_unpack_frombuffer(session, buffer):
        size=len(buffer)
        cmd=0
        return (size,cmd)

    # session_dispatch_packet
    # this method ,call in main thread; and decide woker who will process the packet
    # @param  session.get_sessino_uid()
    # @note: process_packet is user defined module
    @staticmethod
    def session_dispatch_packet(session, packet_cmd, packet_data):
        # print("session_dispatch_packet:", session, packet_cmd,packet_data)
        if packet_cmd == 0:
            session.send(packet_data)
            return
        process_packet.session_dispatch_packet(session, packet_cmd, packet_data)


    @staticmethod
    def task_on_rsp(session_uid, session_data):
        cmd, packet_data = session_data
        logger.debug("task_on_rsp: %s cmd:%d size:%d", str(session_uid), cmd, len(packet_data))
        public_server_interface.send_to_session(session_uid, packet_data)
