#!/usr/bin/env python
# coding=utf-8
##################################################################
#python setup.py install
#python setup.py install --record files.txt
# cat files.txt | xargs rm -rf          #删除这些文件
##################################################################
from setuptools import setup


setup(
    name="pyxxnet",  #pypi中的名称，pip或者easy_install安装时使用的名称
    version="1.0",
    author="Tazzhang",
    author_email="406878851@qq.com",
    description=("This is a framework of network programming"),
    license="GPLv3",
    keywords="network eventloop",
    url="",
    packages=['pyxxnet3'],  # 需要打包的目录列表

    # 需要安装的依赖
    install_requires=[

    ],

    # 添加这个选项，在windows下Python目录的scripts下生成exe文件
    # 注意：模块与函数之间是冒号:
    entry_points={'console_scripts': [
        # 'redis_run = DrQueue.RedisRun.redis_run:main',
    ]},

    # long_description=read('README.md'),
    classifiers=[  # 程序的所属分类列表
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    # 此项需要，否则卸载时报windows error
    zip_safe=False
)
