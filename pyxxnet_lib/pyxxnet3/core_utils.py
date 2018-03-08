#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   core_utils.py
#
#   201706 定义基于epoll的 tcpserver
#
######################################################## #
# reload(sys)
# sys.setdefaultencoding("utf-8")

import os
import sys
import socket
import struct
import site
import platform
import time

def print_python_envinfo():
    print ("-----get_python_envinfo------")
    print (site.getsitepackages())
    print (os.__file__)
    print (sys.version)
    print (platform.platform())
    print (sys.platform)
    if sys.platform != 'win32':
        print ( get_host_info() )


def get_host_info():
    import socket
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    s="======================\n"
    s += "Who are you?\n"
    s += "I am {0},from ip:{1}\n".format(myname,myaddr)
    s += "\n==============\n"
    return s


def is_python3():
    return sys.version[0] == '3'


# 毫秒级别时间戳
def get_tick_count():
    current_time=time.time()
    return int(round(current_time * 1000))


# 秒级别的时间戳
def get_timestamp():
    return int(time.time())


# 毫秒级别时间戳
def get_m_timestamp():
    return int(time.time() * 1000)


def wait(s=0.01):
    time.sleep(s)


def parent_dir_name():
    cwd = os.getcwd()
    cwd = cwd.replace('\\', '/')
    pos = cwd.rfind('/')
    if pos == -1:
        return cwd
    return cwd[pos + 1:]


def current_project_index():
    s = parent_dir_name()
    num = ""
    for i in range(1, len(s) + 1):
        a = s[-i]
        if a.isdigit():
            num = a + num
        else:
            break
    if not num:
        return 0
    num = int(num)
    return num


def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return value  # Instance of str


def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8')
    else:
        value = bytes_or_str
    return value  # Instance of bytes


def file2str(file_name):
    if not os.path.exists(file_name):
        return ""
    with open(file_name, 'r') as f:
        return to_str(f.read().strip())


def dec2hex(dec):
    s = hex(dec)
    return s[2:]


def normalbytes(total_bytes, total_ms):
    if total_ms == 0:
        return "error net io"
    speed = float(total_bytes) / float(total_ms)
    speed = speed * 1000
    if speed < 1024:
        return "{0:0.1f}Bytes/s".format(speed)
    if 1024 <= speed < 1048576:
        return "{0:0.1f}KB/s".format(speed / 1024)
    return "{0:0.1f}MB/s".format(speed / 1048576)


def enc_64bit(a, b):
    c = a << 32 | b
    return c


def dec_64bit(c):
    a = c >> 32
    a = int(a)
    b = c & 0x00000000ffffffff
    b = int(b)
    return a, b


def calculate_size(s=""):
    type_dic = {
        "c": 1,
        "b": 1,
        "B": 1,
        "h": 2,
        "H": 2,
        "i": 4,
        "I": 4,
        "Q": 8,
    }
    a = 0
    for ch in s:
        if ch not in type_dic:
            print ("cannot find type:{0}".format( ch)    )
            return
        a += type_dic[ch]
    return a




def IpStr2NetInt(IpStr):
    return struct.unpack( "I",socket.inet_aton(IpStr)  )[0]

def IpStr2HostInt(IpStr):
    return socket.ntohl(  IpStr2NetInt(IpStr)  )
def NetInt2IpStr(NetInt):
    #return HostInt2IpStr( socket.ntohl(NetInt) )
    return socket.inet_ntoa( struct.pack('I',NetInt)  )
def HostInt2IpStr(HostInt):
    return NetInt2IpStr( socket.htonl(HostInt)  )

def main():
   ip="127.0.0.1"
   print("IpStr2NetInt:", IpStr2NetInt(ip) )
   print("IpStr2HostInt:", IpStr2HostInt(ip))
   print ( NetInt2IpStr( 349496679) )
   print ( HostInt2IpStr( 1574977140) )

if __name__ == '__main__':
    main()