#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   public_server_interface.py
#
#   201706 对外开放的server接口；
#   sudo tcpdump -i any port 9414  -nnA
######################################################## #
import logging

managerLogger = logging.getLogger("managerLogger")
logger = logging.getLogger()
from . import base_server
from .main_loop import InterruptableTaskLoop
from . import core_utils

import os
import sys

if core_utils.is_python3():
    import subprocess as  commands
else:
    import commands


class PARAM:
    baseserver = base_server.BaseServer()


# @定义在队列里传输的对象
class MsgObject(object):
    def __init__(self, session_uid=None, session_data=None):
        self.msg_id = 0
        self.msg_mst = 0
        self.session_uid = session_uid
        self.session_data = session_data


# @初始化服务器
def server_init(appcore_interface):
    core_utils.print_python_envinfo()
    if sys.version_info.major == 2:
        if sys.version_info.minor < 7:
            print("not support the python version for ({0})".format(sys.version))
            sys.exit(2)
    if not appcore_interface:
        print("server_init() failed;@param appcore_interface,cannot be null;")
        sys.exit(1)
    base_server.PARAM.appcore_interface = appcore_interface


# @运行服务器
def server_startAsForver(timeout=0.1):
    managerLogger.debug("server_startAsForver;timeout:%f", timeout)
    InterruptableTaskLoop(PARAM.baseserver, timeout).startAsForver()


# @判断服务器是否正在运行
def server_isRunning():
    work_process_count = len(PARAM.baseserver.workers)
    master_pid = core_utils.file2str('run/master.pid')
    if not master_pid:
        # print "master_pid NULL"
        return False
    worker_pids = [master_pid]
    for i in range(work_process_count):
        worker_pid_file = 'run/worker_{0}.pid'.format(i)
        worker_pid = core_utils.file2str(worker_pid_file)
        if worker_pid:
            worker_pids.append(worker_pid)
            # print "workerid:",worker_pid,len(worker_pid)

    # print worker_pids
    cmd = 'pidof {0}'.format(base_server.PARAM.appcore_interface.python)
    results = commands.getoutput(cmd)
    # print results
    if not results:
        return False

    for pid in worker_pids:
        if pid not in results:
            return False
    return True


# @杀死服务器
def server_exit(work_process_count=1024):
    # work_process_count = len(PARAM.baseserver.workers)
    master_pid = core_utils.file2str('run/master.pid')
    if not master_pid:
        # print "master_pid NULL"
        return False
    worker_pids = [master_pid]
    for i in range(work_process_count):
        worker_pid_file = 'run/worker_{0}.pid'.format(i)
        worker_pid = core_utils.file2str(worker_pid_file)
        if worker_pid:
            worker_pids.append(worker_pid)
        else:
            break
            # print "workerid:",worker_pid,len(worker_pid)

    for pid in worker_pids:
        print("-------------------------------------")
        cmd = 'pidof {0}'.format(base_server.PARAM.appcore_interface.python)
        results = commands.getoutput(cmd)
        if not results:
            print("No Python Process is running")
            return

        if len(worker_pids) == 1:
            killcmd = 'kill -9 {0}'.format(pid)
        else:
            killcmd = 'kill {0}'.format(pid) if master_pid == pid else 'kill -9 {0}'.format(pid)
        i = 0
        while True:
            print(i, cmd, "->", results, " ->", pid)
            if (pid not in results) or i >= 8:
                break

            print(i, killcmd, commands.getstatusoutput(killcmd))
            core_utils.wait(2)
            results = commands.getoutput(cmd)
            if not results:
                break
            i += 1
        print("Close pid:", pid)


# @监控服务器的运行
def server_monit():
    while True:
        if server_isRunning:
            # print "OK"
            core_utils.wait(15)
            continue
        server_exit()
        core_utils.wait(15)
        os.popen("./start.sh")
        core_utils.wait(15)


# @sessionid标识着唯一的session对象，可能是一个id组合
# @底层提供该接口
def send_to_session(sessionid, data):
    return PARAM.baseserver.send_to_session(sessionid, data)


# @which标识着一类后端服务,这里是具体的某一类，这一类的服务，可能由一个连接池组成，包含很多endpoint
# @底层提供该接口
def send_to_endpoint(which, data):
    return PARAM.baseserver.send_to_endpoint(which, data)


# @使用在主进程中,指派任务到Worker中处理
# @底层提供该接口
def send_to_taskQ(m):
    return PARAM.baseserver.send_to_taskQ(m)


# @使用在Worker进程中，回馈结果给主进程
# @底层提供该接口
def send_to_feedbackQ(m):
    return PARAM.baseserver.send_to_feedbackQ(m)
