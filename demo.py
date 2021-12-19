# -*- coding:utf-8 -*-

__author__ = 'linxinloningg'

import traceback

"""自定义的类"""
from EmQuantAPI import *
from core.scheduler_task import timetask
from core.storage import Dataoperation, Exceloperation
from core.strategy import Brinline, Rowcolumn, Doublemov, CCIselect, Grid, \
    Smallmv, Overnight, MACD_KDJ
from core.spider import RealDataSpider, DailymarketSpider, PalSpider

from qywechatbot import BotsendMsg

from datetime import date, datetime
from threading import Thread
from time import sleep


def mainCallback(quantdata):
    """
    mainCallback 是主回调函数，可捕捉如下错误
    在start函数第三个参数位传入，该函数只有一个为c.EmQuantData类型的参数quantdata
    :param quantdata:c.EmQuantData
    :return:
    """
    print("mainCallback", str(quantdata))
    # 登录掉线或者 登陆数达到上线（即登录被踢下线） 这时所有的服务都会停止
    if str(quantdata.ErrorCode) == "10001011" or str(quantdata.ErrorCode) == "10001009":
        print("您的帐户已断开连接。如果需要，您可以在此处强制自动登录。")
    # 行情登录验证失败（每次连接行情服务器时需要登录验证）或者行情流量验证失败时，会取消所有订阅，用户需根据具体情况处理
    elif str(quantdata.ErrorCode) == "10001021" or str(quantdata.ErrorCode) == "10001022":
        print("您的所有csq订阅已停止。")
    # 行情服务器断线自动重连连续6次失败（1分钟左右）不过重连尝试还会继续进行直到成功为止，遇到这种情况需要确认两边的网络状况
    elif str(quantdata.ErrorCode) == "10002009":
        print("您的所有csq订阅已停止，重新连接6次失败。")
    # 行情订阅遇到一些错误(这些错误会导致重连，错误原因通过日志输出，统一转换成EQERR_QUOTE_RECONNECT在这里通知)，正自动重连并重新订阅,可以做个监控
    elif str(quantdata.ErrorCode) == "10002012":
        print("csq订阅在出现错误时中断，自动重新连接并请求。")
    # 资讯服务器断线自动重连连续6次失败（1分钟左右）不过重连尝试还会继续进行直到成功为止，遇到这种情况需要确认两边的网络状况
    elif str(quantdata.ErrorCode) == "10002014":
        print("您的所有cnq订阅已停止，重新连接6次失败。")
    # 资讯订阅遇到一些错误(这些错误会导致重连，错误原因通过日志输出，统一转换成EQERR_INFO_RECONNECT在这里通知)，正自动重连并重新订阅,可以做个监控
    elif str(quantdata.ErrorCode) == "10002013":
        print("cnq订阅在出现错误时中断，自动重新连接并请求。")
    # 资讯登录验证失败（每次连接资讯服务器时需要登录验证）或者资讯流量验证失败时，会取消所有订阅，用户需根据具体情况处理
    elif str(quantdata.ErrorCode) == "10001024" or str(quantdata.ErrorCode) == "10001025":
        print("您的所有cnq订阅已停止。")
    else:
        pass


def startCallback(message):
    print("[EmQuantAPI Python]", message)
    return 1


def csqCallback(quantdata):
    """
    csqCallback 是csq订阅时提供的回调函数模板。该函数只有一个为c.EmQuantData类型的参数quantdata
    :param quantdata:c.EmQuantData
    :return:
    """
    print("csqCallback,", str(quantdata))


def cstCallBack(quantdata):
    """
    cstCallBack 是日内跳价服务提供的回调函数模板
    """
    for i in range(0, len(quantdata.Codes)):
        length = len(quantdata.Dates)
        for it in quantdata.Data.keys():
            print(it)
            for k in range(0, length):
                for j in range(0, len(quantdata.Indicators)):
                    print(quantdata.Data[it][j * length + k], " ", end="")
                print()


def cnqCallback(quantdata):
    """
    cnqCallback 是cnq订阅时提供的回调函数模板。该函数只有一个为c.EmQuantData类型的参数quantdata
    :param quantdata:c.EmQuantData
    :return:
    """
    # print ("cnqCallback,", str(quantdata))
    print("cnqCallback,")
    for code in quantdata.Data:
        for k in range(0, len(quantdata.Data[code])):
            print(quantdata.Data[code][k])


try:
    # 调用登录函数（激活后使用，不需要用户名密码）
    loginResult = c.start("ForceLogin=1", '', mainCallback)
    if loginResult.ErrorCode != 0:
        print("登录失败")
        exit()
    else:
        print("登录成功")

    # 判断是否为交易日
    if getdateformtoday(1) == date.today().strftime("%Y/%m/%d"):

        # 早间任务线程列表创建
        threadMorningtasks = list()

        # 爬虫初始化
        DailymarketSpider = DailymarketSpider()
        RealDataSpider = RealDataSpider()

        # 文件操作类初始化
        Dataoperation = Dataoperation()

        # Excel文件操作类初始化
        Exceloperation = Exceloperation('data.xlsx')

        # 企业微信机器人初始化
        BotsendMsg = BotsendMsg()

        # 线程创建
        # 行业轮动策略
        Rowcolumnrotation = Rowcolumn(Dataoperation, DailymarketSpider, Exceloperation)
        threadMorningtasks.append(Thread(target=Rowcolumnrotation.run))
        # 双均线策略
        Doublemovaverage = Doublemov(Dataoperation, Exceloperation)
        threadMorningtasks.append(Thread(target=Doublemovaverage.run))
        # CCI顺势选股策略
        CCIStockselection = CCIselect(Dataoperation, Exceloperation)
        threadMorningtasks.append(Thread(target=CCIStockselection.run))
        # 布林线选股策略
        Brinlineregression = Brinline(Dataoperation, Exceloperation)
        threadMorningtasks.append(Thread(target=Brinlineregression.run))
        # 小市值选股策略
        Smallmarketvalue = Smallmv(Dataoperation, Exceloperation)
        threadMorningtasks.append(Thread(target=Smallmarketvalue.run))
        # 一夜持股法选股策略
        Overnightshareholding = Overnight(Dataoperation, DailymarketSpider, Exceloperation)
        # 定时为每个交易日下午2点半执行
        timetask(Overnightshareholding.run, 14, 30)

        # 支付宝模拟股票爬虫
        AlipalSpider = PalSpider(BotsendMsg)

        print("等待8点45分开启早间任务")
        BotsendMsg.send_msg_txt("等待8点45分开启早间任务")
        while True:
            # 当时间到达8点45分时启动早间任务
            if int(datetime.now().strftime("%H")) == 8 and int(
                    datetime.now().strftime("%M")) >= 45 or int(datetime.now().strftime("%H")) > 8:

                # 线程全启动
                BotsendMsg.send_msg_txt("现时为{}，启动早间任务！".format(datetime.now()))
                for num in range(len(threadMorningtasks)):
                    threadMorningtasks[num].start()
                # 可有可无的阻塞，阻塞有可能造成某线程崩溃，主线程崩溃
                """for num in range(len(threadstasks)):
                    threadstasks[num].join()"""
                break
            sleep(1)

        """日间交易策略编写"""


        def grid_sell(tradingstrategy):
            while True:
                tradingstrategy.run(60)


        def macdpluskdj_buy(tradingstrategy):
            while True:
                tradingstrategy.run(60)


        def healthstatus(Bot):
            while True:
                if datetime.now().strftime("H") in [10, 11, 13, 14]:
                    print("程序仍在运行正常")
                    Bot.send_msg_txt("程序仍在运行正常")


        """日间交易策略编写"""
        while True:
            # 等待九点到来，推送消息
            if int(datetime.now().strftime("%H")) == 9 and int(
                    datetime.now().strftime("%M")) >= 00 or int(datetime.now().strftime("%H")) > 9:
                # 发送通知消息，提示交易操作开始
                t = Thread(target=BotsendMsg.messagenotification, args=['Msg', Dataoperation])
                t.start()
                """# 可有可无的阻塞，阻塞等待上面的消息发送完毕，再执行以下任务
                t.join()"""
                break
            sleep(1)

        # 定时在九点25分开始
        print("等待九点25分到来")
        while True:

            if int(datetime.now().strftime("%H")) == 9 and int(
                    datetime.now().strftime("%M")) >= 25 or int(datetime.now().strftime("%H")) > 9:
                # 日间任务线程列表创建
                threadDaytasks = list()
                # 报告程序运行状况函数
                threadDaytasks.append(Thread(target=healthstatus, args=[BotsendMsg]))
                print("一天的交易操作开始")
                # 获取今日交易数据,需在获取数据并已经成功写入之后
                datadict = Exceloperation.read()

                print("buydata:" + str(datadict['buy']))
                print("selldata:" + str(datadict['sell']))
                content = '\n\n今天需要交易购买的股票为:' + str(datadict['buy'])
                content += '\n\n今天需要交易卖出的股票为:' + str(datadict['sell'])

                BotsendMsg.send_msg_txt(content)
                # 实时数据交易策略(需排除空数据)
                if datadict['sell']:
                    BotsendMsg.send_msg_txt("网格交易法正在执行{}策略".format('卖'))
                    Gridtransaction = Grid(datadict['sell'], 'sell', RealDataSpider, AlipalSpider)
                    threadDaytasks.append(Thread(target=grid_sell, args=[Gridtransaction]))

                # 实时数据交易策略（需排除空数据）
                if datadict['buy']:
                    BotsendMsg.send_msg_txt("MACD叠加KDJ正在执行{}策略".format('买'))
                    MACDplusKDJtransaction = MACD_KDJ(datadict['buy'], 'buy', RealDataSpider,
                                                      AlipalSpider)
                    threadDaytasks.append(Thread(target=macdpluskdj_buy, args=[MACDplusKDJtransaction]))

                # 设置线程为守护线程
                for num in range(len(threadDaytasks)):
                    threadDaytasks[num].setDaemon(True)
                # 线程全启动
                for num in range(len(threadDaytasks)):
                    threadDaytasks[num].start()
                # 可有可无的阻塞，阻塞有可能造成某线程崩溃，主线程崩溃，同时，阻塞情况下，将无法回到主程序
                # 当线程存在死循环函数时，join将导致无法回到主线程的情况
                """for num in range(len(threadstasks)):
                    threadstasks[num].join()"""

                break

            sleep(1)

        print("开始正常运转")
        # 在下午3点结束
        while True:
            # 并在之后推送消息提示
            if int(datetime.now().strftime("%H")) == 14 and int(
                    datetime.now().strftime("%M")) >= 45 or int(datetime.now().strftime("%H")) > 14:
                BotsendMsg.send_msg_txt("现在时间为{}，{}".format("14:45", Dataoperation.read2txt('Msg/一夜持股策略.txt')))
            if int(datetime.now().strftime("%H")) == 15 and int(
                    datetime.now().strftime("%M")) >= 00 or int(datetime.now().strftime("%H")) > 15:
                BotsendMsg.send_msg_txt("一天的交易操作结束")
                print("一天的交易操作结束")
                break

            sleep(1)
    else:
        print("今天不是交易日，不执行程序")
    # 退出
    data = logoutResult = c.stop()
except Exception as ee:
    print("error >>>", ee)
    traceback.print_exc()
else:
    print("程序结束")
