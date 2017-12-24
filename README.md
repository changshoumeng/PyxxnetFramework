# pyxxnet_project
This is a pure python implementation of network services development framework.

这是一个纯Python实现的网络服务框架，支持多进程运行，通过消息队列把任务散发到多个进程做执行，
内置对网络收发指标的在线统计，使用做一些内部的微服务。


你可以自己设计协议，使得这个网络服务框架成为一个httpservice，当然更强大的是，几行代码就可以让你
拥有自定义的服务。


本服务的网络库叫做pyxxnet3，位于pyxxnet_lib目录下，你可以执行python setup.py install 使得它安装于python
的sitepackage目录下，或者你可以直接把pyxxnet3目录拷贝到你的工程目录下。

如何使用这个网络库？
最简单的例子，是参照：sample_echoserver下的代码，大部分的网络服务的实现都与sample_echoserver代码相似，
或者说，你可以选择直接把sample_echoserver复制一份，基于此做开发。

就是这样的简单。

python pyechosvr.py 启动一个服务

python my_test.py 就开启了一个测试客户端，快来尝试下这个项目吧！

我更期望您直接与我联系，一起探讨有趣的python编程。







