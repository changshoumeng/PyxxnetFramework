import os
import sys
import site
import platform


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


print_python_envinfo()