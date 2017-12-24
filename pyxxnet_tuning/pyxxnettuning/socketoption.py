# -*- coding: utf-8 -*-
# !/usr/bin/env python
###################################################
# Teaching Wisedom to My Computer,
# Please Call Me Croco,Fuck Your Foolishness.
# Linux 内核调优
##################################################
import socket




def test_tcpsocketopt(option_desc="",socket_option=socket.SO_SNDBUF,option_value=1024):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    old_value = s.getsockopt(socket.SOL_SOCKET, socket_option)
    s.setsockopt(socket.SOL_SOCKET, socket_option, option_value)
    new_value = s.getsockopt(socket.SOL_SOCKET, socket_option)
    print "test_tcpsocketopt,{0},old:{1} willset:{2} new:{3}".format(option_desc,old_value,option_value,new_value)
    return new_value

def test_udpsocketopt(option_desc="",socket_option=socket.SO_SNDBUF,option_value=1024):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    old_value = s.getsockopt(socket.SOL_SOCKET, socket_option)
    s.setsockopt(socket.SOL_SOCKET, socket_option, option_value)
    new_value = s.getsockopt(socket.SOL_SOCKET, socket_option)
    print "test_udpsocketopt,{0},old:{1} willset:{2} new:{3}".format(option_desc,old_value,option_value,new_value)
    return new_value


def test_keeplive():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    keepalive_v=s.getsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE)
    s.getsockopt(socket.SOL_SOCKET,socket.SO)
    print "SO_KEEPALIVE:",keepalive_v


def main():
    sendbufsize_list=[]
    recvbufsize_list=[]
    for val in [0,1,1024,4096,5000,1024*16,1024*16+1,1024*1024,1024*1024,1024*1024] :
        ret=test_tcpsocketopt("socket.SO_SNDBUF", socket.SO_SNDBUF, val)
        sendbufsize_list.append(ret)
        ret=test_tcpsocketopt("socket.SO_RCVBUF", socket.SO_RCVBUF, val)
        recvbufsize_list.append(ret)
        print

    print "-"*10
    sendbufsize_list.sort()
    recvbufsize_list.sort()
    print "sendbufsize,min:{0} max:{1}".format(sendbufsize_list[0], sendbufsize_list[-1])
    print "recvbufsize,min:{0} max:{1}".format(recvbufsize_list[0], recvbufsize_list[-1])



    print "-" * 10



    pass


if __name__ == '__main__':
    #main()
    test_keeplive()
