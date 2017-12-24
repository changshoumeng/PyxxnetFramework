#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python -m pyxxnet3.tcpproxy


import logging.config

logging.config.fileConfig(r"D:\tmp\1\textwithtags_model\conf\logging_debug.conf")
logger = logging.getLogger()
import sys
import random
from . import public_server_interface
from . import pyxxconstant
from . import public_server_callback


class APP_CORE_HANDLER(public_server_callback.ServerCallback):
    endpoint_ids = [i for i in range(1)]
    endpoint_session_map = {}
    session_endpoint_map = {}

    def __init__(self):
        pass

    @staticmethod
    def my_servername():
        return "my_tcp_proxy"

    @staticmethod
    def listenconfig_get(key=""):  # 10.10.2.143
        c = {"addresslist": [("0.0.0.0", 10004, 0)], "eventloop": "select", }
        return c[key]

    @staticmethod
    def connectconfig_get(key=""):
        server_addr_list = [("127.0.0.1", 9414, i) for i in APP_CORE_HANDLER.endpoint_ids]
        c = {"addresslist": server_addr_list, "eventloop": "select", }
        # return ""
        return c[key]

    @staticmethod
    def workerconfig_get(key=""):
        c = {"workercount": 0, }
        return c[key]

    # @return: len(buffer),0  <size,cmd>
    @staticmethod
    def session_unpack_frombuffer(session, buffer):
        # print("session_unpack_frombuffer:",session,buffer)
        buflen = len(buffer)
        return (buflen, 1)

    @staticmethod
    def session_dispatch_packet(session, packet_cmd, packet_data):
        session_uid = session.get_session_uid()
        # print("session_dispatch_packet:", session_uid, packet_cmd,packet_data)
        tmp_ep_list = [i for i in APP_CORE_HANDLER.endpoint_ids if i not in APP_CORE_HANDLER.endpoint_session_map]
        # print("tmp_ep_list:",tmp_ep_list,APP_CORE_HANDLER.endpoint_session_map)
        if len(tmp_ep_list) == 0:
            print("session_dispatch_packet;but no endpoint to use")
            return
        if session_uid in APP_CORE_HANDLER.session_endpoint_map:
            which = APP_CORE_HANDLER.session_endpoint_map[session_uid]
            APP_CORE_HANDLER.endpoint_session_map[which] = session_uid
        else:
            which = random.choice(tmp_ep_list)
            APP_CORE_HANDLER.session_endpoint_map[session_uid] = which
            APP_CORE_HANDLER.endpoint_session_map[which] = session_uid
        logger.debug("req {0}>{1} len:{2}".format(session_uid, which, len(packet_data)))
        public_server_interface.send_to_endpoint(which, packet_data)

    @staticmethod
    def endpoint_unpack_frombuffer(endpoint, buffer):
        buflen = len(buffer)
        return (buflen, 1)

    @staticmethod
    def endpoint_dispatch_packet(endpoint, packet_cmd, packet_data):
        which = endpoint.which
        if which not in APP_CORE_HANDLER.endpoint_session_map:
            print("endpoint_dispatch_packet;cannot find session by which:{0}".format(which))
            return

        session_uid = APP_CORE_HANDLER.endpoint_session_map.get(which)
        logger.debug("rsp {0}>{1} len:{2}".format(which, session_uid, len(packet_data)))
        public_server_interface.send_to_session(session_uid, packet_data)
        pass

    @staticmethod
    def session_keeplive(session, status=0):
        if status == pyxxconstant.LIVE_STATUS.LIVE_STATUS_END:
            session_uid = session.get_session_uid()
            print("session_keeplive;disconnect;{0}".format(session))
            if session_uid in APP_CORE_HANDLER.session_endpoint_map:
                which = APP_CORE_HANDLER.session_endpoint_map[session_uid]
                del APP_CORE_HANDLER.session_endpoint_map[session_uid]
                del APP_CORE_HANDLER.endpoint_session_map[which]
        pass

    @staticmethod
    def endpoint_keeplive(endpoint, status=0):
        if status == pyxxconstant.LIVE_STATUS.LIVE_STATUS_END:
            print("endpoint_dispatch_packet;disconnect;{0}".format(endpoint))
            which = endpoint.which
            if which in APP_CORE_HANDLER.endpoint_session_map:
                session_uid = APP_CORE_HANDLER.endpoint_session_map[which]
                del APP_CORE_HANDLER.session_endpoint_map[session_uid]
                del APP_CORE_HANDLER.endpoint_session_map[which]


def check_argv():
    if len(sys.argv) == 2:
        if sys.argv[1] == "stop":
            public_server_interface.server_exit()
            sys.exit(1)
        if sys.argv[1] == "monit":
            public_server_interface.server_monit()
            sys.exit(2)


def main():
    check_argv()
    public_server_interface.server_init(APP_CORE_HANDLER)
    public_server_interface.server_startAsForver(timeout=0.01)


if __name__ == '__main__':
    main()
    pass
