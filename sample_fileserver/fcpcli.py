#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import time
import os


class PARAM:
    service_ip_list = ["127.0.0.1"]
    service_port = 9444
    MAX_RECV_SIZE = 8196
    MAX_SEND_SIZE = 4096
    CURRENT_DIR="client"


def recvfile(s,filename):
    print filename
    print "server ready, now client rece file~~"
    f = open(filename, 'wb')
    while True:
        data = s.recv(1024*16)
        if data == 'EOF':
            print "recv file success!"
            break
        f.write(data)
    f.close()



def sendfile(s,service_address,filename):
    fsize = os.path.getsize(filename)
    print "Service:{0} is reading,fsize:{1}".format(service_address,fsize)

    f = open(filename, 'rb')
    t=0
    last_percent=0
    while True:
        data = f.read(PARAM.MAX_SEND_SIZE)
        if not data:
            break
        t += len(data)
        percent = (t*100)/fsize
        if last_percent < percent+10:
            pass
        else:
            print "send  size:{0},finish:{1}%".format( len(data),percent)
            last_percent = percent
        s.sendall(data)
    f.close()
    s.sendall('EOF')
    print "send ok,total size is {0}".format(t)


def confirm(s, client_command):
    s.send(client_command)
    data = s.recv(PARAM.MAX_RECV_SIZE)
    if data == 'ready':
        return True
    return False


def main():
    print ("=" * 100)
    print ("Hello,This is FileClient,You can upload file to server as below:")
    socket_list=[]
    for ip in PARAM.service_ip_list:
        port = PARAM.service_port
        service_address=(ip,port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(service_address)
            socket_list.append(  (s,service_address)  )
            print "Connected OK to  service:{0}".format(service_address)
        except socket.error, e:
            print "Connected failed to {0};socket.error:{1}".format(service_address,e)
            print "Sure that service_address:{0} is real adress???".format(service_address)
    if len(socket_list) == 0:
        print ("Sorry,no service to use,exit")
        return
    print ("-" * 50)
    print ("If you want to exit,please input <q>")
    print ("Usage:")
    print ("put <filename>")
    while True:
        client_command = raw_input(">>")
        if not client_command:
            continue
        if client_command == "q" or client_command=='Q':
            print "exit"
            break
        arr = client_command.split()
        if len(arr) != 2:
            print "Usage is invalid;your cmd is :{0}".format(client_command)
            continue
        action, filename = arr[0],arr[1]
        if not os.path.exists(filename):
            print "File:{0} is not exist".format(filename)
            continue
        if action == 'put':
            for (s,service_address) in socket_list:
                if confirm(s, client_command):
                    sendfile(s,service_address,filename)
                else:
                    print "Service:{0} go wrong,action:put".format(service_address)
        elif action == 'get':
            for (s,service_address) in socket_list:
                if confirm(s, client_command):
                    print PARAM.CURRENT_DIR
                    print filename
                    filename = PARAM.CURRENT_DIR + '/' + os.path.split(client_command)[1]
                    print filename
                    recvfile(s,filename)
                else:
                    print "Service:{0} go wrong,action:get".format(service_address)
        else:
            print "command error! not support the cmd:{0}".format(action)



if __name__ == '__main__':
    main()
