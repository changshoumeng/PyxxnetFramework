#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#   这是一个压力测试程序的客户端：
#       它第一步是建立N个TCP连接，第二步是在每一条连接上尝试一次IO
#       为了使模拟的并发能力达到百万级，请保持客户机的配置如下：
'''
4.10.0-42-generic #16.04.1-Ubuntu   x86_64 GNU/Linux
5G内存/2核心CPU
网卡Speed: 1000Mb/s
ulimit -SHn 1048576
fs.file-max = 2000000
net.ipv4.tcp_mem = 786432 2097152 3145728
net.ipv4.tcp_rmem = 1024 1024 16777216
net.ipv4.tcp_wmem = 1024 1024 16777216
net.core.somaxconn = 10000
net.ipv4.ip_local_port_range = 1024 65535
'''
import traceback
import sys

import threading
import socket,time
import random
socket.setdefaulttimeout(60)


def get_tick_count():
    t = time.time() * 1000
    return int(t)


'''建立一条TCP连接'''
def build_connection(ip, port,connection_list,i):
    addr = (ip, port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    t1 = get_tick_count()
    use_tick=-1
    try:
        #local_addr=("10.10.2.19",1025+i)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        #s.bind( local_addr )
        s.connect(addr)
        use_tick = get_tick_count() - t1
        connection_list.append( (s,use_tick) )
        if (len(connection_list)%1000==0) or (len(connection_list)==1) or use_tick >= 1000:
            print("connect() addr:{0};ok;use_tick:{1};fd:{2};cnt:{3} port:{4}"
                  .format(addr, use_tick,s.fileno(),len(connection_list) ,s.getsockname() ))
        return True
    except socket.error as arg:
        print("connect(failed) addr:{0};ok;use_tick:{1};fd:{2};cnt:{3} error:{4}"
              .format(addr, use_tick, s.fileno(), len(connection_list),arg))
        if arg.errno == 98:
            return True
    return False


'''在一条TCP连接上，做一次IO请求'''
def ioctrl(s,ioctl_list=[]):
    t1 = get_tick_count()
    use_tick = -1
    try:
        flag='a'
        if not s.send(flag):
            print "sendfailed"
            return False
        #print "send:",flag
        result = s.recv(1024)
        #print "recv:",result
        use_tick = get_tick_count() - t1
        if result==flag:
            ioctl_list.append(use_tick)
            return True
    except socket.error as arg:
        print(arg)
    return False

'''在一条TCP连接上，做一次吞吐测试'''
def throughput(s):
    td= IoThread(s)
    td.start()
    return td


def _io_thread_handler(s):
    print("_io_thread_handler socket:{0} begin".format( s.fileno() ))
    data="1"*512
    if not  s.send(data):
        print("_io_thread_handler socket:{0} sendfailed".format(s.fileno()))
        return
    try:
        totalsize = 0
        begintick = get_tick_count()
        for i in xrange(2000000):
            result = s.recv(1024*16)
            # print result
            if not result or result != data:
                print("_io_thread_handler socket:{0} recvzero".format(s.fileno()))
                print (result)
                return

            totalsize += len(result)


            sendlen=s.send(data)
            if sendlen != len(data):
                print("_io_thread_handler socket:{0} sendfailed;sendlen:{1}".format(s.fileno(),sendlen))
                return

            totalsize += sendlen
            usetick = get_tick_count() - begintick
            if usetick>0 and (i==0 or i%1000==0):
                speed = totalsize*1000.0/(usetick*1024)
                tps   =  i*1000.0/(usetick)
                print("_io_thread_handler socket:{0} ;speed:{1};tps:{2}".format(s.fileno(), speed,tps))



    except:
        info = sys.exc_info()
        t = '**************_manager_thread caught exception*************'
        for f, l, func, text in traceback.extract_tb(info[2]):
            t += "\n[file]:{0} [{1}] [{2}] {3}".format(f, l, func, text)
        t += "\n[info]:%s->%s\n" % info[:2]
        print (t)
    finally:
        print("_io_thread_handler socket:{0} end".format(s.fileno()))




class IoThread(threading.Thread):
    def __init__(self,sock):
        threading.Thread.__init__(self)
        self.sock=sock
    def run(self):
        _io_thread_handler(self.sock)




def fenxi_connections(connection_list):
    cnt = len(connection_list)
    item = connection_list[0]
    fd = item[0].fileno()
    tk = item[1]
    port = item[0].getsockname()[1]
    max_fd, min_fd, max_tick, min_tick, avg_tick, total_tick = fd, fd, tk, tk, tk, tk
    min_port, max_port = port, port

    for i in xrange(1, cnt, 1):
        item = connection_list[i]
        fd = item[0].fileno()
        port = item[0].getsockname()[1]
        min_port = min(min_port, port)
        max_port = max(max_port, port)
        tk = item[1]
        max_fd = max(max_fd, fd)
        min_fd = min(min_fd, fd)
        max_tick = max(max_tick, tk)
        min_tick = min(min_tick, tk)
        total_tick += tk
    avg_tick = total_tick * 1.0 / cnt
    print ("conn_test>cnt:{0} fd:{1}-{2} tick:{3}-{4}-{5} port:{6}-{7}".format(cnt, min_fd, max_fd, min_tick, avg_tick,
                                                                               max_tick, min_port, max_port))

def fenxi_ioctl(connection_list):
    cnt = len(connection_list)
    ioctl_list = []
    for (s, t) in connection_list:
        if not ioctrl(s, ioctl_list):
            break
    if len(ioctl_list) < 1:
        print "ioctl failed"
        return
    else:
        use = sum(ioctl_list) * 1.0 / len(ioctl_list)
        print "io_test>avg time:{0} succ:{1} total:{2}".format(use, len(ioctl_list), cnt)

'''测试一条连接上的吞吐量'''
def fenxi_throughput(connection_list):
    iothreads=[]
    for (s, t) in connection_list[:20]:
        td = throughput(s)
        iothreads.append(td)
    for td in iothreads:
        td.join()



def main():
    connection_list=[]
    for i in xrange(200):
        port=random.randint(9000,9999)
        if not build_connection("10.10.2.204",port,connection_list,i):
            break
    cnt = len(connection_list)
    if cnt <1:
        return

    fenxi_connections(connection_list)
    # time.sleep(10)
    fenxi_ioctl(connection_list)
    # time.sleep(10)
    fenxi_throughput(connection_list)
    raw_input(">>END.")
    pass


if __name__ == '__main__':
    t1 = get_tick_count()
    main()
    use = get_tick_count()-t1
    print ("Everything is Good;use:",use)

