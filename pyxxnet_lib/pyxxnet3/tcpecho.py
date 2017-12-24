# -*- coding: utf-8 -*-
#
#
#  from pyxxnet import tcpecho
#  tcpecho.server(1444)
#
#

from socket import *
from time import ctime

setdefaulttimeout(60)


def server(port):
    addr = ("", port)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(addr)
    sock.listen(1024)
    print("create socket:{0};listen in {1}".format(sock.fileno(), addr))
    while True:
        print('waiting for connecting at {0}'.format(addr))
        client, addr = sock.accept()
        print('accept client:{0} addr:{1} ', client.fileno(), addr)
        while True:
            print("recv...")
            try:
                data = client.recv(1024 * 16)
            except Exception as  e:
                print('caught exception; client:{0} addr:{1} ', client.fileno(), addr)
                print(e)
                client.close()
                break
            if not data:
                print('recv 0; client:{0} addr:{1} ', client.fileno(), addr)
                break
            print("recv:", data)
            s = 'Hi,you send me :[%s] %s' % (ctime(), data.decode('utf8'))
            client.send(s.encode('utf8'))
            print([ctime()], ':', data.decode('utf8'))

    print("-----------------------------")
    sock.close()
    print("END")
