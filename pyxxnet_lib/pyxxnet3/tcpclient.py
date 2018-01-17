# -*- coding: utf-8 -*-
# from pyxxnet import tcpclient
# tcpclient.prob1("127.0.0.1", 1444)

import socket
import sys

import core_utils

socket.setdefaulttimeout(5)


def prob1(ip, port):
    addr = (ip, port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("socket() fileno:{0}".format(s.fileno()))
    print("connect() addr:{0} ... ...".format(addr))
    t1 = core_utils.get_tick_count()
    try:
        s.connect(addr)
        use_tick = core_utils.get_tick_count() - t1
        print("connect() addr:{0};ok;use_tick:{1}".format(addr, use_tick))
    except socket.error as arg:
        print(arg)
        # use_tick = core_utils.get_tick_count() - t1
        # errno, err_msg = arg
        # print("connect server(%s) failed: %s, errno=%d use_tick=%d" % (addr, err_msg, errno, use_tick) )
        sys.exit(1)

    while True:
        inp = raw_input("please input:\n>>>")
        print(":::", inp)
        if inp == "q":
            print("END")
            s.sendall(inp)
            sys.exit(1)
        else:
            t1 = core_utils.get_tick_count()
            bytes_sent = s.sendall(inp)
            print("sendall:", bytes_sent, "data:", inp)
            result = s.recv(1024 * 8)
            use_tick = core_utils.get_tick_count() - t1
            print("use_tick=%d userecv:%s" % (use_tick, result))


if __name__ == '__main__':
    prob1("127.0.0.1",8303)
