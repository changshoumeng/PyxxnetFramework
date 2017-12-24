#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#
######################################################## #

import logging

logger = logging.getLogger()

import process_packet



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
        cmd, packet = msg.session_data
        rsp=process_packet.process_task(worker,cmd,packet)
        if rsp:
            msg.session_data = cmd, rsp
            return msg

