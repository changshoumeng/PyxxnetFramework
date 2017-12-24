pyxxnet_project

Hi,This is a pure python implementation of network services development framework.

A clever person solves a problem. A wise person avoids it

Please call Me programming devil.


    这是一个纯Python实现的网络服务框架，支持多进程运行，通过消息队列把任务散发到多个进程做执行，
内置对网络收发指标，任务执行情况的在线统计，适合用以做一些内部的微服务。

    这份代码的设计原型是一份久经线上项目考验的linux c++网络服务框架，换以python重写的初衷是易于开发
一个测试用的压测框架。    

    你可以自己设计http2.0协议，使得这个网络服务框架成为一个httpservice；你也可以自己设计通信协议，得到满
足你项目需求的高性能的服务。 当然更强大的是，几行代码就可以让你拥有自定义的服务。

    本服务的网络库叫做pyxxnet3，位于pyxxnet_lib目录下，你可以执行python setup.py install 使得它安装于python
的sitepackage目录下，或者你可以直接把pyxxnet3目录拷贝到你的工程目录下。

    pyxxnet3在python 2.7以上 或者python 3.x的版本，都得到顺利运行。后续将补充一些可视化的管理后台，与对比测试，
优化。

    如何使用这个网络库？
    
最简单的方法，是参照例子：sample_echoserver下的代码，大部分的网络服务的实现都与sample_echoserver代码相似，或者说，
你可以选择直接把sample_echoserver复制一份，基于此做开发。

    就是这样的简单。

    python pyechosvr.py 启动一个服务

    python my_test.py 就开启了一个测试客户端，快来尝试下这个项目吧！

我更期望您直接与我联系，一起探讨有趣的python编程。联系的QQ 406878851，关注C10M问题，更关心Python的变现。
    
    https://github.com/changshoumeng/pyxxnet_project.git
