#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#
######################################################## #
import json
import logging
import sys
import traceback

from pyxxnet3 import public_server_interface
import app_core_handler


logger = logging.getLogger()

# @pram session
# @pram packet_cmd
# @pram packet_data
def session_dispatch_packet(session, packet_cmd, packet_data):
    # print("session_dispatch_packet():",packet_data)
    sessionid = session.get_session_uid()
    workercount = app_core_handler.APP_CORE_HANDLER.workerconfig_get("workercount")
    if workercount == 0:
        rsp = process_task(None, packet_cmd, packet_data)
        if rsp:
            public_server_interface.send_to_session(sessionid, rsp)
        return
    # transid = _my_trans_map.add(sessionid, packet)
    public_server_interface.send_to_taskQ(public_server_interface.MsgObject(sessionid, (packet_cmd, packet_data)))


def process_task(worker, packet_cmd, packet_data):
    logger.debug("process_task invalid cmd:{0} packet_data:{1}".format( packet_cmd,packet_data))
    return packet_data