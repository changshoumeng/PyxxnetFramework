#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   Teach Wisedom To Machine.
#   Please Call Me Programming devil.
#   Model Name: message_pipe.py
######################################################## #
import logging
import multiprocessing

from . import core_param
from . import core_utils

if core_utils.is_python3():
    import queue as Queue
else:
    import Queue

statuslogger = logging.getLogger("statusLogger")


class MsgObject(object):
    def __init__(self, session_uid=None, session_data=None):
        self.msg_id = 0
        self.msg_mst = core_utils.get_m_timestamp()
        self.session_uid = session_uid
        self.session_data = session_data


# 可反馈似的的消息队列
class FeedbackLikeMessageQueue(object):
    def __init__(self):
        self.mp_message_queue = multiprocessing.JoinableQueue()
        self.mp_feedback_queue = multiprocessing.JoinableQueue()
        self.msgid = 1

    def push_task(self, m):
        qsize = self.mp_message_queue.qsize()
        if qsize >= core_param.MAX_CUSUMER_PIPE_REFUSE_QSIZE:
            statuslogger.critical("push_task error;full;qsize is %d;msgid is %d", qsize, self.msgid )
            return
        if qsize >= core_param.MAX_CUSUMER_PIPE_WARNING_QSIZE:
            statuslogger.critical("push_task warning;qsize is %d;msgid id %d", qsize,self.msgid)

        m.msg_id = self.msgid
        self.msgid += 1
        m.msg_mst = core_utils.get_m_timestamp()
        self.mp_message_queue.put(m)
        statuslogger.debug("push_task<%d,%d> qsize:%d", m.msg_id, m.msg_mst, self.mp_message_queue.qsize())

    def push_feedback(self, m):
        qsize = self.mp_feedback_queue.qsize()
        if qsize >= core_param.MAX_FEEDBACK_PIPE_REFUSE_QSIZE:
            statuslogger.critical("push_feedback error;full;qsize is %d", qsize)
            return
        if qsize >= core_param.MAX_FEEDBACK_PIPE_WARNING_QSIZE:
            statuslogger.critical("push_feedback warning;qsize is %d", qsize)
        self.mp_feedback_queue.put(m)

    def pop_task(self):
        try:
            m = self.mp_message_queue.get(block=True, timeout=core_param.MAX_CUSUMER_PIPE_BLOCK_TIMEOUT)
            self.on_req(m)
            self.mp_message_queue.task_done()
            return True
        except Queue.Empty:
            pass
        return False

    def pop_feedback(self):
        try:
            m = self.mp_feedback_queue.get(block=True, timeout=core_param.MAX_FEEDBACK_PIPE_BLOCK_TIMEOUT)
            self.on_rsp(m)
            self.mp_feedback_queue.task_done()
            return True
        except Queue.Empty:
            pass

        return False

    def size(self):
        return (self.mp_message_queue.qsize(), self.mp_feedback_queue.qsize())

    def on_req(self, m):
        raise NotImplementedError()

    def on_rsp(self, m):
        raise NotImplementedError()
