#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   core_status.py
#
#   201706 参数定义 要观察的状态
#
######################################################## #
import logging
statuslogger = logging.getLogger("statusLogger")
from . import core_utils

max_notify_event_count = 0
max_socket_fileno = 0
max_doaccept_count = 0  # 一次accept通知，可以accept的最大次数
max_sendonce_size = 0
max_recvonce_size = 0


class RunningData(object):
    def __init__(self):
        self.recv_packet_begin = 0
        self.recv_packet_end = 0
        self.recv_packet_count = 0
        self.recv_packet_bytes = 0
        self.send_packet_begin = 0
        self.send_packet_end = 0
        self.send_packet_count = 0
        self.send_packet_bytes = 0
        self.last_report_tm=core_utils.get_tick_count()

    def recv(self, recv_size):
        if self.recv_packet_begin == 0:
            self.recv_packet_begin = core_utils.get_tick_count()
        self.recv_packet_bytes += recv_size
        self.recv_packet_count += 1

    def send(self, send_size):
        if self.send_packet_begin == 0:
            self.send_packet_begin = core_utils.get_tick_count()
        self.send_packet_bytes += send_size
        self.send_packet_count += 1

    def report(self):
        nowtick = core_utils.get_tick_count()
        if nowtick<self.last_report_tm+30:
            return
        self.last_report_tm=nowtick
        sendtick = nowtick - self.send_packet_begin
        recvtick = nowtick - self.recv_packet_begin
        send_byte_speed = 0
        send_count_speed = 0
        recv_byte_speed = 0
        recv_count_speed = 0
        if self.send_packet_begin > 0 and sendtick > 0:
            send_byte_speed = core_utils.normalbytes(self.send_packet_bytes, sendtick)
            send_count_speed = float(self.send_packet_count * 1000) / float(sendtick)
        if self.recv_packet_begin > 0 and recvtick > 0:
            recv_byte_speed = core_utils.normalbytes(self.recv_packet_bytes, recvtick)
            recv_count_speed = float(self.recv_packet_count * 1000) / float(recvtick)
        t = "sendbs:{0} sendcs:{1:0.1f} rbs:{2} rcs:{3:0.1f}".format(send_byte_speed, send_count_speed, recv_byte_speed,
                                                                     recv_count_speed)
        statuslogger.info(t)


runingdata=RunningData()