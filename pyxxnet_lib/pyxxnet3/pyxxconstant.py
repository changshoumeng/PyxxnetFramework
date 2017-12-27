#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   pyxxconstant.py
#
#   201710 定义网络库依赖的核心的常量，这数据是不可修改的，类似于C语言的枚举类型;
#       要保证此文件不依赖于其他文件，它将大量地被其他文件依赖
######################################################## #



class CONNECT_STATUS(object):
    '''
    定义常量，描述client_status的值
    '''
    CONNECT_SUCC = 0  # 连接是好的
    CONNECT_DOING = 1  # 客户端正在连接
    CONNECT_FAIL = 2  # 客户端连接服务端，一连接就失败了
    CONNECT_LOSELIVE = 3  # 超时失活
    CONNECT_CLI_WILLCONNECT = 10  # 客户端将要连接
    CONNECT_CLI_WILLCLOSED = 11  # 将要被关闭，是因为客户端断开了连接，或者检查连接无效了
    CONNECT_SER_WILLCLOSED = 12  # 将要被关闭，是因为该连接上检查到不符合逻辑行为
    CONNECT_SYS_WILLCLOSED = 13  # 将要被关闭，是因为系统资源准备不足,异常，程序BUG
    CONNECT_CLOSED = 20  # 已经关闭


############################################################################

class CONNECT_TYPE(object):
    '''
    定义常量，connection_type
    '''
    IS_CONNECTOR = 0
    IS_ACCEPTOR = 1
    IS_LISTENTOR = 2


class LIVE_STATUS(object):
    LIVE_STATUS_BEGIN = 0x00 #第一次connect，连接成功了的状态；或者，第一次accept一个会话时的状态。
    LIVE_STATUS_KEEPLIVE = 0x01 #周期性触发的包；或者收到客户端周期性心跳包触发
    LIVE_STATUS_REPAIR = 0x02
    LIVE_STATUS_END = 0x03  #连接被kill了
    LIVE_STATUS_FAILED=0x04 #第一次connect就失败了
