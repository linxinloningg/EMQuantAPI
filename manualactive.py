# -*- coding:utf-8 -*-

__author__ = 'linxinloningg'

from EmQuantAPI import *
import platform

# 手动激活范例(单独使用)
# 获取当前安装版本为x86还是x64
# 编辑日期：2018-09-29
data = platform.architecture()

if data[0] == "64bit":
    bit = "x64"
elif data[0] == "32bit":
    bit = "x86"

data1 = platform.system()
if data1 == 'Linux':
    system1 = 'linux'
    lj = c.setserverlistdir("libs/" + system1 + '/' + bit)
elif data1 == 'Windows':
    system1 = 'windows'
    lj = c.setserverlistdir("libs/" + system1)
elif data1 == 'Darwin':
    system1 = 'mac'
    lj = c.setserverlistdir("libs/" + system1)
else:
    pass

data = c.manualactivate("13286515438", "qQ1602368639", "email=1602368639@qq.com")
if data.ErrorCode != 0:
    print("manualactivate failed, ", data.ErrorMsg)
