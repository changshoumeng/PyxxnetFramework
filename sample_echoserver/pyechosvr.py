#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging.config

import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import pyxxnet3
from pyxxnet3 import public_server_interface
import app_core_handler,param

logging.config.fileConfig(param.log_file)

def check_argv():
    if len(sys.argv) == 2:
        if sys.argv[1] == "stop":
            public_server_interface.server_exit()
            sys.exit(1)
        if sys.argv[1] == "monit":
            public_server_interface.server_monit()
            sys.exit(2)

def print_version():
    print ("---------------------------")
    print ("author:{0}".format( pyxxnet3.__author__))
    print ("version:{0}".format(pyxxnet3.__version__ ))


def main():
    print_version()
    public_server_interface.server_init(app_core_handler.APP_CORE_HANDLER)
    check_argv()
    public_server_interface.server_startAsForver(timeout=0.001)


if __name__ == '__main__':
    main()
    pass
