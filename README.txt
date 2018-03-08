项目名称：	PyxxnetFramework  基于python的网络框架							
代码路径：	https://github.com/changshoumeng/PyxxnetFramework							
项目描述：

	"     这是一个纯Python实现的网络服务化框架，基于这套服务框架已经开发了类似天气服务、推送服务、文本识别服务等线上系统，这对于期望把python做的算法模型快速服务化的需求是一个可行方案。
     
     这个框架从代码栈上讲，从下到上包含三层：
     1.对系统api的包装层：实现对原生接口的抽象，适配不同的操作系统，对上提供基本模块
       eventloop，iohandler，worker，messagepipe
     2.网络通信层：实现基于eventloop的异步io，基于mailbox的并发模型，对上提供通信组件
       listener，connector，acceptor，logicworker
     3.服务化框架层：提供对baseserver的抽象，使得开发者只需专注业务实现，修改配置文件就能启动。
       frontworker，backworker，logicworker   
     
     本服务的网络库叫做pyxxnet3，位于pyxxnet_lib目录下，你可以执行python setup.py install 使得它安装于python
的sitepackage目录下，或者你可以直接把pyxxnet3目录拷贝到你的工程目录下。
      
如何使用这个网络库？
    
    最简单的方法，是参照例子：sample_echoserver下的代码，大部分的网络服务的实现都与sample_echoserver代码相似，或者说，
你可以选择直接把sample_echoserver复制一份，基于此做开发。

    就是这样的简单。

    python pyechosvr.py 启动一个服务

    python my_test.py 就开启了一个测试客户端，快来尝试下这个项目吧！

我更期望您直接与我联系，一起探讨有趣的python编程。联系的QQ 406878851，关注C10M问题，更关心Python的变现。
    
    https://github.com/changshoumeng/pyxxnet_project.git
"							
代码结构：	
    pyxxnet_lib	包括pyxxnet3等核心的网络库						
	pyxxnet_manager	记录对pyxxnet的配置管理的日志						
	pyxxnet_tuning	记录开发pyxxnet过程，所做的网络性能调优的过程						
	sample_client	测试pyxxnet的样例客户端						
	sample_echoserver	基于pyxxnet开发的echoserver，所做的一些压力测试正是在这个项目里。						
