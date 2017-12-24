#!/usr/bin/env python
# -*- coding: utf-8 -*-
import SocketServer
import time
import os
import socket


class PARAM:
    host = "0.0.0.0"
    port = 9444
    MAX_RECV_SIZE = 8196
    CURRENT_DIR="fileroot"


class MyFtpServer(SocketServer.BaseRequestHandler):

    def recvfile(self, filename):
        filename=filename.strip()
        print ("Connection:{0},recvfile:{1},Begin".format(self.client_address,filename))
        with open(filename,'wb') as f:
            self.request.send('ready')
            while True:
                data = self.request.recv(PARAM.MAX_RECV_SIZE * 10)
                if not data:
                    print ("Lost a connection from :{0},While recvfile ...".format(self.client_address))
                    break
                if data == 'EOF':
                    print ("Connection:{0},recvfile:{1},End".format(self.client_address, filename))
                    break
                f.write(data)


    def sendfile(self, filename):
        print "starting send file!"
        self.request.send('ready')
        time.sleep(1)
        f = open(filename, 'rb')
        while True:
            data = f.read(1024*16)
            if not data:
                break
            self.request.sendall(data)
        f.close()
        time.sleep(1)
        self.request.send('EOF')
        print "send file success!"


    def handle(self):
        print ("Got a connection from :{0}".format(self.client_address))
        while True:
            try:
                data = self.request.recv(PARAM.MAX_RECV_SIZE)
                if not data:
                    print ("Lost a connection from :{0}".format(self.client_address))
                    break
                else:
                    action, filename = data.split()
                    if action == "put":
                        filename = PARAM.CURRENT_DIR + '/' + os.path.split(filename)[1]
                        self.recvfile(filename)
                    elif action == 'get':
                        self.sendfile(filename)
                    else:
                        print ("Error at connection from :{0} data:{2}".format(self.client_address,data))
                        continue
            except socket.error as  msg:
                print ("Got a connection from :{0} ,caught socket.error:{1}".format(self.client_address,msg))
                return




def main():

    address=(PARAM.host,PARAM.port)
    print ("="*100)
    print ("Hello,This is FileService,Providing file upload and download")
    print ("Service is working at {0}".format(address))
    print ("FileRoot is at {0}".format( PARAM.CURRENT_DIR))
    if not os.path.isdir( PARAM.CURRENT_DIR ):
        os.mkdir(PARAM.CURRENT_DIR)
    s = SocketServer.ThreadingTCPServer(address, MyFtpServer)
    s.serve_forever()
    print ("Service is end")

if __name__ == "__main__":
    main()




