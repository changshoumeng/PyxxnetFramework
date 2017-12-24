#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   core_param.py
#
#   201706 参数定义
#
######################################################## #

NULL_BYTE = b''

MAX_SESSION_COUNT = 1024
MAX_TIMEOUT_INTVAL = 20
MAX_EVENT_WAITTIME = 0.01
MAX_LISTEN_BACKLOG = 1024

MAX_RECV_BUFFER_SIZE = 16 * 1024
MAX_SEND_BUFFER_SIZE = 16 * 1024
MAX_KEEPLIVE_TIME = 600

MAX_RECV_COUNT = 128
MAX_PROCESS_RECVBUFFER_TIMEOUT = 1000

MAX_FEEDBACK_PIPE_WARNING_QSIZE = 2000
MAX_FEEDBACK_PIPE_REFUSE_QSIZE = 10000
MAX_FEEDBACK_PIPE_BLOCK_TIMEOUT = 0.1

MAX_CUSUMER_PIPE_WARNING_QSIZE = 2000
MAX_CUSUMER_PIPE_REFUSE_QSIZE = 10000
MAX_CUSUMER_PIPE_BLOCK_TIMEOUT = 0.1
