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
from pyxxnet3 import pyxxconstant
from pyxxnet3 import public_server_interface
import process_packet,app_worker,param



class APP_CORE_HANDLER2(public_server_callback.ServerCallback):
    endpoint_ids = [i for i in range(5)]
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
        return ""

    @staticmethod
    def connectconfig_get(key=""):
        server_addr_list = [("10.10.2.204", 8303, i) for i in APP_CORE_HANDLER2.endpoint_ids]
        c = {"addresslist": server_addr_list, "eventloop": "select", }
        return c[key]

    @staticmethod
    def workerconfig_get(key=""):
        c = {"workercount": 0, }
        return c[key]


    @staticmethod
    def endpoint_unpack_frombuffer(endpoint, buffer):
        (size, cmd) = ( len(buffer) ,0)
        return (size, cmd)


    @staticmethod
    def endpoint_keeplive(endpoint, status=0):
        if status == pyxxconstant.LIVE_STATUS.LIVE_STATUS_KEEPLIVE:
            pass
            return
        if status == pyxxconstant.LIVE_STATUS.LIVE_STATUS_BEGIN:
            data="1"*102400
            endpoint.send(data)
            return
        if status == pyxxconstant.LIVE_STATUS.LIVE_STATUS_END:
            pass
            return

    '''
    tcpdump -i enp0s3 -nnA 'src port 8303'
    '''
    @staticmethod
    def endpoint_dispatch_packet(endpoint, packet_cmd, packet_data):
        endpoint.send(packet_data)
