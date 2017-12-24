#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   kernelparameters.py
#
#   定义需要调整的内核参数
#
######################################################## #


tasks = [
    ('open files', 'ulimit -n'),
    ('core file size', 'ulimit -c'),
    ('max user processes', 'ulimit -u'),
    ('max memory size', 'ulimit -m'),
    ('fs.file-max', 'cat /proc/sys/fs/file-max'),
    ('epoll-event-max', 'cat /proc/sys/fs/epoll/max_user_watches'),
    ('listen-queue-size', 'cat /proc/sys/net/core/somaxconn'),
    ('ipv4.tcp_max_syn_backlog', 'cat /proc/sys/net/ipv4/tcp_max_syn_backlog'),
    ('net.core.rmem_default', 'cat /proc/sys/net/core/rmem_default'),
    ('net.core.wmem_default', 'cat /proc/sys/net/core/wmem_default'),
    ('net.core.rmem_max', 'cat /proc/sys/net/core/rmem_max'),
    ('net.core.wmem_max', 'cat /proc/sys/net/core/wmem_max '),
    ('net.ipv4.tcp_rmem', 'cat /proc/sys/net/ipv4/tcp_rmem'),
    ('net.ipv4.tcp_wmem', 'cat /proc/sys/net/ipv4/tcp_wmem'),
    ('net.ipv4.tcp_mem', 'cat /proc/sys/net/ipv4/tcp_mem'),
    ('net.ipv4.ip_local_port_range ', 'cat /proc/sys/net/ipv4/ip_local_port_range'),
    ('net.ipv4.tcp_timestamps', 'cat /proc/sys/net/ipv4/tcp_timestamps'),
    ('net.ipv4.tcp_tw_recycle', 'cat /proc/sys/net/ipv4/tcp_tw_recycle'),
]
