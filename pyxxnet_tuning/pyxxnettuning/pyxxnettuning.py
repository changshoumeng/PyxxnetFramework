#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   A clever person solves a problem. A wise person avoids it
#   Please call Me programming devil.
#
#   pyxxnettuning.py
#
#
#
######################################################## #


import commands
import kernelparameters
import os
import socket
from collections import OrderedDict
from multiprocessing import cpu_count
import json

def get_json_str(json_dict):
    js_str=json.dumps(json_dict,sort_keys=False,separators=(',',':'))
    return js_str

def split_string(string_data='',sep=' '):
    str_arr0 = []
    str_arr1 = string_data.split(sep)
    for s in str_arr1:
        if not s:
            continue
        if s != sep:
            str_arr0.append(s)
    return  str_arr0


def compare_result( result1="", result2=""):
    result_arr1 = split_string(result1, sep=' ')
    result_arr2 = split_string(result2, sep=' ')
    if len(result_arr1) != len(result_arr2):
        return ""
    result_arr = []
    is_change = False
    for i in xrange(len(result_arr1)):
        r1 = result_arr1[i]
        r2 = result_arr2[i]
        if r1.isdigit() and r2.isdigit():
            if int(r1) < int(r2):
                result_arr.append(r2)
                is_change =True
            else:
                result_arr.append(r1)
    if not is_change:
        return ""

    return ' '.join(result_arr)


def test_tcpsocketopt(option_desc="",socket_option=socket.SO_SNDBUF,option_value=1024):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    old_value = s.getsockopt(socket.SOL_SOCKET, socket_option)
    s.setsockopt(socket.SOL_SOCKET, socket_option, option_value)
    new_value = s.getsockopt(socket.SOL_SOCKET, socket_option)
    #print "test_tcpsocketopt,{0},old:{1} willset:{2} new:{3}".format(option_desc,old_value,option_value,new_value)
    return new_value


def get_realsocketbufsize():
    sendbufsize_list=[]
    recvbufsize_list=[]
    for val in [0,1,1024,4096,5000,1024*16,1024*16+1,1024*1024,1024*1024*5,1024*1024*10] :
        ret=test_tcpsocketopt("socket.SO_SNDBUF", socket.SO_SNDBUF, val)
        sendbufsize_list.append(ret)
        ret=test_tcpsocketopt("socket.SO_RCVBUF", socket.SO_RCVBUF, val)
        recvbufsize_list.append(ret)

    sendbufsize_list.sort()
    recvbufsize_list.sort()
    #print "sendbufsize,min:{0} max:{1}".format(sendbufsize_list[0], sendbufsize_list[-1])
    #print "recvbufsize,min:{0} max:{1}".format(recvbufsize_list[0], recvbufsize_list[-1])
    return (sendbufsize_list[0], sendbufsize_list[-1],recvbufsize_list[0], recvbufsize_list[-1])

#dmesg | grep -i numa
def get_cpu_info():
    data = OrderedDict()
    cpuinfo = OrderedDict()
    procinfo = OrderedDict()
    nprocs = 0
    model_name = set()
    cpu_mhz = set()
    cache_size=set()
    cache_alignment = set()
    address_size=set()
    with open('/proc/cpuinfo') as f:
        for line in f:
            if not line.strip():
                # end of one processor
                cpuinfo['proc%s' % nprocs] = procinfo
                nprocs = nprocs + 1
                # Reset
                procinfo = OrderedDict()
            else:
                if len(line.split(':')) == 2:
                    k=line.split(':')[0].strip()
                    v= line.split(':')[1].strip()
                    procinfo[k] =v
                    if k=='model name':
                        model_name.add(v)
                    elif k=='cpu MHz':
                        cpu_mhz.add(v)
                    elif k=='cache size':
                        cache_size.add(v)
                    elif k=='cache_alignment':
                        cache_alignment.add(v)
                    elif k=='address sizes':
                        address_size.add(v)
                else:
                    procinfo[line.split(':')[0].strip()] = ''

    if nprocs != cpu_count():
        print("get_cpu_info() warn that nprocs:{0} cpu_count():{1}".format(nprocs,cpu_count()))
    data["cpu_count"] = nprocs
    lastkey='proc%d'%(nprocs-1)
    data['cpu_cores'] = cpuinfo[lastkey]["cpu cores"]
    data['model_name'] =list(model_name)
    data['cpu_mhz'] = list(cpu_mhz)
    data['cache_size'] = list(cache_size)
    data['cache_alignment'] = list(cache_alignment)
    data['address_size'] = list(address_size)
    cmd="getconf LONG_BIT"
    data["LONG_BIT"]=commands.getoutput(cmd)
    return get_json_str(data)


def get_mem_info():
    data=OrderedDict()
    meminfo = OrderedDict()
    with open('/proc/meminfo') as f:
        for line in f:
            meminfo[line.split(':')[0]] = line.split(':')[1].strip()
    data['MemTotal'] =meminfo['MemTotal']
    data['MemFree'] = meminfo['MemFree']
    data['Shmem'] = meminfo['Shmem']
    return get_json_str(data)




class KernelTuning(object):
    def __init__(self,suggest_file='KernelTuning10W.txt'):
        self._task_list = []
        self._result_file='KernelTuning.txt'
        self._suggest_file=suggest_file
        pass
    def _add_task(self,key,cmd,result):
        self._task_list.append(  (key,cmd,result) )

    def _put_line(self,line):
        print line
        with open(self._result_file, 'a') as f:
            f.write(line+'\n')
    def _put_done(self):
        line="===================================\n"
        self._put_line(line)


    def print_task_list(self):
        if os.path.exists(self._result_file):
            os.remove(self._result_file)

        self._suggest_dict = {}
        self._suggest_list = []
        if os.path.exists(self._suggest_file):
            with open(self._suggest_file,'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    if not  line:
                        continue
                    key_arr=line.split('\t')
                    if len(key_arr) != 3:
                        continue
                    k,c,r = key_arr[0][1:-1],key_arr[1],key_arr[2]
                    self._suggest_dict[k]=r

        self.read_devinfo()

        self._put_line("[Linux Kernel]")
        self.read_realsocketbufsize()

        for task in self._task_list:
            k,c,r=task[0],task[1],task[2]
            line="'{0}'\t'{1}'\t{2}".format(k,c,r)
            self._put_line(line)
            if k in self._suggest_dict:
                result = compare_result(result1=r,result2=self._suggest_dict[k])
                if result:
                    r = result
                    line = "'{0}'\t'{1}'\t{2}".format(k, c, r)
                    self._suggest_list.append(line)
                else:
                    pass
            else:
                pass
        self._put_done()
        line= "[suggest_list {0}]".format(len(self._suggest_list))
        self._put_line(line)
        for line in self._suggest_list:
            self._put_line(line)
        self._put_done()

    def read_realsocketbufsize(self):
        a = get_realsocketbufsize()
        b = map(lambda x: str(x), a)
        line = "'{0}'\t'{1}'\t{2}".format("realsocketbufsize", "sendbufsize:recvbufsize", ' '.join(b))
        self._put_line(line)

    def read_devinfo(self):
        self._put_line("[my machine info]")
        cmd = "cat /proc/version"
        status, result = commands.getstatusoutput(cmd)
        self._put_line(result)

        cmd = "uname -a"
        status, result = commands.getstatusoutput(cmd)
        self._put_line(result)

        result = get_cpu_info()
        self._put_line(result)

        result = get_mem_info()
        self._put_line(result)
        self._put_done()



    def exec_cmd(self,key='',cmd=''):
        status, result = commands.getstatusoutput(cmd)
        if status != 0:
            result = 'status={0} result={1}'.format(status,result)
        self._add_task(key,cmd,result)

    def read_kernel_arguments(self,tasks):
        for t in tasks:
            self.exec_cmd( t[0],t[1] )
        self.print_task_list()
        print

    def set_kernel_arguments(self,is_temp=True):
        pass

    def make_suggest_report(self):
        pass



def main():
    k = KernelTuning()
    k.read_kernel_arguments(kernelparameters.tasks)

if __name__ == '__main__':
    main()
