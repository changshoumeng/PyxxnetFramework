#!/usr/bin/env python
# -*- coding: utf-8 -*-
AUTHOR = "zhangtao"
NICK = "changshoumeng"
VERSION = "V2.0.0"
CONTACT = "QQ:406878851"

##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   version.py
#
#   Author: zhangtao
#   Nick: Changshoumeng
#   QQ:40678851
#   Purpose of Develop the Library:  pyxxnet3
#       实现一个纯Python实现的高并发高性能，并且跨平台易于创建服务的网络库。
#       期望基于此库，应该很容易实现一个网络服务；应该可把Windows下可以运行的代码直接拷贝到linux下即可运行；
#
#
#   历史版本变更记录：
######################################################## #

VERSION_V1_0_0 = '''
#V1.0.0   初创版本   20161201        zhangtao
#   ---------------------------------------
#   基于对既有单台主机支撑10万级别并发连接的C++网络库的 压测程序开发，以及对关联的socket参数调优，linux内核调优的探索性
#       工作，汇集了工作中涉及到底零碎的PYTHON脚本，整理集合成此库
#   首先设计了一个event_loop
#     其次实现了基于select模型的event_loop
#           实现了基于epoll模型的event_loop
#                在python2.7的环境下开发测试通过
'''

VERSION_V2_0_0 = '''
#   V2.0.0   初创版本   20171001        zhangtao
#   ---------------------------------------
#   基于要实现文本分类要使用Keras深度学习库，而Windows环境下只有python3才支持tenserflow库，所以开始把此pyxxnet迁移到python3
#       保持python2.7下也兼容可运行。
'''




