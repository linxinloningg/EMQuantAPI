# -*- coding:utf-8 -*-
__author__ = 'linxinloningg'

from sklearn import linear_model
from core.quota import q
from EmQuantAPI import *
import os.path
import numpy as np
import pandas as pd
from time import sleep
from datetime import date

import math


class Brinline:
    """
    布林线均值回归策略:
    当股价向上突破上界时，为卖出信号，当股价向下突破下界时，为买入信号。
    """

    def __init__(self, Dataoperation, Exceloperation, accounts="", commission_ratio=0.0001, N=5, quota=100000,
                 period=7):
        """
        :param Dataoperation: 文件操作类
        :param Exceloperation: EXcel文件操作类
        :param accounts: 已持仓股票东财代码列表（'600031.SH,300059.SZ'）
        :param commission_ratio: 交易费用
        :param N: 需要推荐多少个符合策略的股票
        :param quota: 资金配额
        :param period: 权重计算周期
        """
        self.Dataoperation = Dataoperation
        self.Exceloperation = Exceloperation
        self.codes = sectorCodes()
        self.commission_ratio = commission_ratio
        self.num = N
        self.accounts = accounts
        self.quota = quota
        self.period = period
        self.content = None

        print("目前根据布林线均值回归策略已持仓：" + str(self.accounts))
        self.content = "目前根据布林线均值回归策略已持仓：" + str(self.accounts)

    def getvalue(self):
        # 获取股票的前一天布林线上中下值列表，用于今天的布林线回归策略选股
        MAMID, MAUPPER, MALOWER = q.index_boll(self.codes, 1)
        PRECLOSE = {}
        # 获取前一天股票收盘价，用于今天开盘前进行布林线均值回归策略选股
        data = c.css(self.codes, "PRECLOSE", "TradeDate={},AdjustFlag=1".format(getdateformtoday(-1)))
        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request css Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    for i in range(0, len(data.Indicators)):
                        data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                        PRECLOSE[code] = data.Data[code][i]

        Purchase_D = {}
        Sellout_D = {}
        # 当股价向上突破上界时，为卖出信号，当股价向下突破下界时，为买入信号。
        # 选取股价突破布林线上值，或者跌破布林线下值的股票，并与布林值进行相减，得到差值
        for code in self.codes:
            if round(float(PRECLOSE[code]), 2) >= round(float(MAUPPER[code][0]), 2):
                Sellout_D[code] = float(PRECLOSE[code]) - float(MAUPPER[code][0])

            if round(float(PRECLOSE[code]), 2) <= round(float(MALOWER[code][0]), 2):
                Purchase_D[code] = float(MALOWER[code][0]) - float(PRECLOSE[code])

        Purchase = list()
        Sellout = list()

        """# 剔除异常值
        Purchase_std = np.std(list(Purchase_D.values()), ddof=1)
        Sellout_std = np.std(list(Sellout_D.values()), ddof=1)
        for code, value in Purchase_D.items():
            if value >= Purchase_std:
                del Purchase_std[code]
        for code, value in Sellout_D.items():
            if value >= Sellout_std:
                del Sellout_D[code]"""

        # 从大到小排序
        # 将差值大小进行排序，差值越大，即突破布林线上值或跌破布林线下值越明显，应给予推荐或者止损
        for bigvalue in sorted(list(Purchase_D.values()), reverse=True):
            for code, value in Purchase_D.items():
                if value == bigvalue:
                    Purchase.append(code)

        for bigvalue in sorted(list(Sellout_D.values()), reverse=True):
            for code, value in Sellout_D.items():
                if value == bigvalue:
                    Sellout.append(code)

        return Purchase, Sellout

    def run(self):
        print("开始进行布林线回归策略选股")
        Purchase, Sellout = self.getvalue()
        print("布林线回归策略选股共选出{}个适合股票购买,为{}".format(len(Purchase), Purchase))
        self.content += "\n布林线回归策略选股共选出{}个适合股票购买,为:".format(len(Purchase)) + str(Purchase)
        Clearance = list()
        Position = list()
        for account in self.accounts:

            if account in Purchase:
                Purchase.remove(account)

            if account in Sellout:
                Clearance.append(account)

        Position.extend(Purchase[:self.num])
        print("布林线回归策略选股前{}推荐股票为：{}".format(self.num, Position))
        print("根据此策略已有持仓，建议卖出的股票为：{}".format(Clearance))
        self.content += "\n布林线回归策略选股前{}推荐股票为：".format(self.num) + str(Position)
        self.content += "\n根据此策略已有持仓，建议卖出的股票为：" + str(Clearance)
        print("布林线回归策略选股以完成")

        # 获取推荐股票的昨收价
        Currentpricelist = list()
        Yieldlist = list()
        for code in Position:
            for price in q.index_close(code, 1).values():
                Currentpricelist.append(price[0])
            for profit in q.index_maavgprofit(code, self.period).values():
                Yieldlist.append(profit[0])

        # 根据收益率算权重（按选定的权重计算周期计算）
        Weightlist = list()
        share = round(1 / sum(range(1, self.num + 1)), 1)
        for value in Yieldlist:
            Weightlist.append(sorted(Yieldlist).index(value) * share)

        # 根据昨收和配额，按权重算出购买股数
        # 剔除某个股股价过高的导致配额不够用的情况

        Numberofshares = 100
        quota = self.quota
        for code in Position:
            if Currentpricelist[Position.index(code)] * Numberofshares >= quota:
                Position.pop(Position.index(code))
                Currentpricelist.pop(Position.index(code))
                print("{}股价过高，超出配额，剔除！".format(code))

        while quota > 0:
            for i in range(0, len(Position)):
                quota -= Currentpricelist[i] * Numberofshares * (1 + Weightlist[i])

            Numberofshares += 100
        data = {}
        data.setdefault('buy', {})
        data.setdefault('sell', {})
        for code in Position:
            data['buy'][code] = [Currentpricelist[Position.index(code)], int(math.ceil(
                Numberofshares * (1 + Weightlist[Position.index(code)]) / 100.0)) * 100
                                 ]
        for code in Clearance:
            data['sell'][code] = '现价平仓'

        data.setdefault('布林线回归策略', str(date.today()))
        if self.Exceloperation.write(data) is True:
            self.content += '\n成功写入今日布林线回归策略'

        self.Dataoperation.writetxt(self.content, 'Msg/布林线回归策略.txt')
        return data


class Rowcolumn:
    def __init__(self, Dataoperation, DailymarketSpider, Exceloperation, accounts="", commission_ratio=0.0001, N=3,
                 quota=100000,
                 period=7):
        """
        :param Dataoperation: 文件操作类
        :param DailymarketSpider:日常数据爬虫
        :param Exceloperation: EXcel文件操作类
        :param accounts: 已持仓股票东财代码列表（'600031.SH,300059.SZ'）
        :param commission_ratio: 交易费用
        :param N: 需要推荐多少个符合策略的股票
        :param quota: 资金配额
        :param period: 权重计算周期
        """
        self.Dataoperation = Dataoperation
        self.DailymarketSpider = DailymarketSpider
        self.Exceloperation = Exceloperation
        self.codes = sectorCodes()
        self.commission_ratio = commission_ratio
        self.num = N
        self.accounts = accounts
        self.minstocknum = 10
        self.quota = quota
        self.period = period
        self.content = None
        print("目前根据行业轮动策略已持仓：" + str(self.accounts))
        self.content = "目前根据行业轮动策略已持仓：" + str(self.accounts)

    def getplatecode(self):
        platecode = {}
        data = c.css(self.codes, "BLEMIND", "ClassiFication=2")

        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request css Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    for i in range(0, len(data.Indicators)):
                        platecode[code] = data.Data[code][i]
        print("重新获取全股票全板块属性完成")
        self.content += "\n重新获取全股票全板块属性完成"
        return self.Dataoperation.write(platecode, 'platecode')

    def getvalue(self):
        Latestprice, Fluctuationrange, High, Low, Open, Volumeratio, Turnoverrate, Marketvalue, codes = self.DailymarketSpider.run()
        print("涨幅：" + str(Fluctuationrange))
        print("换手率：" + str(Turnoverrate))
        Risingstock = {}
        Fallingstock = {}
        for code, value in Fluctuationrange.items():
            if float(value) > 0:
                Risingstock[code] = float(value)
            else:
                Fallingstock[code] = float(value)
        print("上涨股票代码及涨幅：" + str(Risingstock))
        print("下跌股票代码及跌幅：" + str(Fallingstock))
        Riseingcodes = list(Risingstock.keys())
        Fallingcodes = list(Fallingstock)
        # 剔除换手率小于5的冷门股
        """for code in Riseingcodes:
            if float(Turnoverrate[code]) < 5:
                Riseingcodes.remove(code)
        for code in Fallingcodes:
            if float(Turnoverrate[code]) < 5:
                Fallingcodes.remove(code)"""

        self.content += "全部股票代码总数：" + str(len(codes))

        print("全部股票代码总数：" + str(len(codes)))
        print("上涨股票代码总数：" + str(len(Riseingcodes)))
        self.content += "\n上涨股票代码总数：" + str(len(Riseingcodes))
        print("上涨股票代码：" + str(Riseingcodes))
        print("下跌股票代码总数：" + str(len(Fallingcodes)))
        self.content += "\n下跌股票代码总数：" + str(len(Fallingcodes))
        print("下跌股票代码：" + str(Fallingcodes))

        TotalPlatetype = self.Dataoperation.read('platecode')
        print("全部板块代码：" + str(TotalPlatetype))

        RiseingPlatetype = {}
        for Crawlercode in Riseingcodes:
            for Dongcaicode in list(TotalPlatetype.keys()):
                # 处理东财代码 （000001.SZ）  爬虫返回的代码为301071
                if Crawlercode.replace('"', '') == Dongcaicode.split('.')[0]:
                    RiseingPlatetype[Dongcaicode] = TotalPlatetype[Dongcaicode]
        print("全部上涨的板块代码：" + str(RiseingPlatetype))

        FallingPlatetype = {}
        for Crawlercode in Fallingcodes:
            for Dongcaicode in list(TotalPlatetype.keys()):
                # 处理东财代码 （000001.SZ）  爬虫返回的代码为301071
                if Crawlercode.replace('"', '') == Dongcaicode.split('.')[0]:
                    FallingPlatetype[Dongcaicode] = TotalPlatetype[Dongcaicode]
        print("全部下跌的板块代码：" + str(FallingPlatetype))

        Hotplate = list()
        platelist = list(RiseingPlatetype.values())
        print("共统计有{}个板块".format(len(set(list(TotalPlatetype.values())))))

        Coldplate = list()
        coldplatelist = list(FallingPlatetype.values())

        classplate = set(platelist)
        rate = {}
        for plate in classplate:
            if list(TotalPlatetype.values()).count(plate) > self.minstocknum:
                rate[plate] = platelist.count(plate) / list(TotalPlatetype.values()).count(plate)
        platerate = sorted(list(rate.values()), reverse=True)[:self.num]
        for key, value in rate.items():
            if value in platerate:
                Hotplate.append(key)
        print("热门前三板块：" + str(Hotplate))

        classplate = set(coldplatelist)
        rate = {}
        for plate in classplate:
            if list(TotalPlatetype.values()).count(plate) > self.minstocknum:
                rate[plate] = coldplatelist.count(plate) / list(TotalPlatetype.values()).count(plate)
        platerate = sorted(list(rate.values()), reverse=True)[:self.num]
        for key, value in rate.items():
            if value in platerate:
                Coldplate.append(key)
        print("冷门前三板块：" + str(Coldplate))

        Hotplatecodes = {}
        for plate in Hotplate:
            Hotplatecodes[plate] = list()
            for code, existplate in RiseingPlatetype.items():
                if plate == existplate:
                    Hotplatecodes[plate].append(code)

        Coldplatecodes = {}
        for plate in Coldplate:
            Coldplatecodes[plate] = list()
            for code, existplate in FallingPlatetype.items():
                if plate == existplate:
                    Coldplatecodes[plate].append(code)

        print("前{}上涨板块代码：".format(self.num) + str(Hotplatecodes))
        self.content += "\n前{}上涨板块代码：".format(self.num) + str(Hotplatecodes)
        print("前{}下跌板块代码：".format(self.num) + str(Coldplatecodes))
        self.content += "\n前{}下跌板块代码：".format(self.num) + str(Coldplatecodes)
        for plate in Hotplate:
            print("{}板块共有{}个股票，".format(plate, list(TotalPlatetype.values()).count(plate)))
            print("其中共有{}股票上涨，上涨率为{}".format(len(Hotplatecodes[plate]),
                                             len(Hotplatecodes[plate]) / list(TotalPlatetype.values()).count(
                                                 plate)))
            self.content += "\n{}板块共有{}个股票，".format(plate, list(TotalPlatetype.values()).count(plate))
            self.content += "\n其中共有{}股票上涨，上涨率为{}".format(len(Hotplatecodes[plate]),
                                                         len(Hotplatecodes[plate]) / list(
                                                             TotalPlatetype.values()).count(
                                                             plate))
        for plate in Coldplate:
            print("{}板块共有{}个股票，".format(plate, list(TotalPlatetype.values()).count(plate)))
            print("其中共有{}股票下跌，下跌率为{}".format(len(Coldplatecodes[plate]),
                                             len(Coldplatecodes[plate]) / list(TotalPlatetype.values()).count(
                                                 plate)))
            self.content += "\n{}板块共有{}个股票，".format(plate, list(TotalPlatetype.values()).count(plate))
            self.content += "\n其中共有{}股票下跌，下跌率为{}".format(len(Coldplatecodes[plate]),
                                                         len(Coldplatecodes[plate]) / list(
                                                             TotalPlatetype.values()).count(
                                                             plate))
        Recommendationcode = {}
        for plate, codelist in Hotplatecodes.items():
            scope = {}
            Recommendationcode[plate] = list()
            for Dongcaicode in codelist:
                Crawlercode = '"' + Dongcaicode.split('.')[0] + '"'

                scope[Crawlercode] = Risingstock[Crawlercode]

            # 排序

            ranglist = sorted(list(scope.values()), reverse=True)[:self.num]

            for value in ranglist:
                for Crawlercode, extent in scope.items():
                    if extent == value:
                        # 将爬虫代码转化成东财代码
                        for Dongcaicode in codelist:
                            if Crawlercode == '"' + Dongcaicode.split('.')[0] + '"':
                                Recommendationcode[plate].append(Dongcaicode)
            # 去除因涨停而带来的重复项录入
            Recommendationcode[plate] = set(Recommendationcode[plate])
        self.content += "\n前{}热门板块龙头代码：".format(self.num) + str(Recommendationcode)

        return Recommendationcode

    def run(self):
        Recommendationcode = None
        if os.path.isfile('platecode.csv') is False:
            print("文件不存在")
            if self.getplatecode() is True:
                Recommendationcode = self.getvalue()
                print("*" * 200)
                print("前{}热门板块龙头代码：".format(self.num) + str(Recommendationcode))
                # 获取推荐股票的昨收价

        else:
            print("文件存在")
            Recommendationcode = self.getvalue()
            print("*" * 200)
            print("前{}热门板块龙头代码：".format(self.num) + str(Recommendationcode))
            # 获取推荐股票的昨收价

        data = {}
        data.setdefault('buy', {})
        data.setdefault('sell', {})
        for plate, codelist in Recommendationcode.items():
            Position = list(codelist)
            Clearance = list()
            Currentpricelist = list()
            Yieldlist = list()
            for code in Position:
                for price in q.index_close(code, 1).values():
                    Currentpricelist.append(price[0])
                for profit in q.index_maavgprofit(code, self.period).values():
                    Yieldlist.append(profit[0])

            # 根据收益率算权重（按选定的权重计算周期计算）
            Weightlist = list()
            share = round(1 / sum(range(1, self.num + 1)), 1)
            for value in Yieldlist:
                Weightlist.append(sorted(Yieldlist).index(value) * share)

            # 根据昨收和配额，按权重算出购买股数
            # 剔除某个股股价过高的导致配额不够用的情况

            Numberofshares = 100
            quota = self.quota / self.num
            for code in Position:
                if Currentpricelist[Position.index(code)] * Numberofshares >= quota:
                    Position.pop(Position.index(code))
                    Currentpricelist.pop(Position.index(code))
                    print("{}股价过高，超出配额，剔除！".format(code))

            while quota > 0:
                for i in range(0, len(Position)):
                    quota -= Currentpricelist[i] * Numberofshares * (1 + Weightlist[i])

                Numberofshares += 100

            for code in Position:
                data['buy'][code] = [Currentpricelist[Position.index(code)], int(math.ceil(
                    Numberofshares * (1 + Weightlist[Position.index(code)]) / 100.0)) * 100
                                     ]
            for code in Clearance:
                data['sell'][code] = '现价平仓'

        data.setdefault('行业轮动指标策略', str(date.today()))
        if self.Exceloperation.write(data) is True:
            self.content += '\n成功写入今日行业轮动指标策略'
        self.Dataoperation.writetxt(self.content, 'Msg/行业轮动选股策略.txt')
        return data


class Doublemov:
    """
    双均线策略:
    通过建立m天移动平均线，n天移动平均线，则两条均线必有交点。
    若m>n，n天平均线“上穿越”m天均线则为买入点，反之为卖出点。
    """

    def __init__(self, Dataoperation, Exceloperation, accounts="", commission_ratio=0.0001, N=5, quota=100000,
                 period=7):
        """
        :param Dataoperation: 文件操作类
        :param accounts: 已持仓股票东财代码列表（'600031.SH,300059.SZ'）
        :param commission_ratio: 交易费用
        :param N: 需要推荐多少个符合策略的股票
        :param quota: 资金配额
        :param period: 权重收益计算周期
        """
        self.Dataoperation = Dataoperation
        self.Exceloperation = Exceloperation
        self.codes = sectorCodes()
        self.commission_ratio = commission_ratio
        self.num = N
        self.accounts = accounts
        self.quota = quota
        self.period = period

        print("目前根据双均线策略已持仓：" + str(self.accounts))
        self.content = "目前根据双均线策略已持仓：" + str(self.accounts)

    def getsuitablestock(self, m, n):
        MA_m = {}
        ma_list = list()
        print("开始获取简单移动平均线数据")
        data = c.css(self.codes, "MA",
                     "TradeDate={},N={},K=3,Boll=1,AdjustFlag=1,Period=1".format(getdateformtoday(-3), m))
        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request css Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    for i in range(0, len(data.Indicators)):
                        ma_list.append(data.Data[code][i])

        a = 0
        for code in data.Codes:
            MA_m[code] = list()
            for b in range(a, len(ma_list), len(data.Codes)):
                MA_m[code].append(ma_list[b])
            MA_m[code].reverse()
            a += 1

        MA_n = {}
        ma_list = list()
        data = c.css(self.codes, "MA",
                     "TradeDate={},N={},K=3,Boll=1,AdjustFlag=1,Period=1".format(getdateformtoday(-3), n))
        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request css Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    for i in range(0, len(data.Indicators)):
                        ma_list.append(data.Data[code][i])

        a = 0
        for code in data.Codes:
            MA_n[code] = list()
            for b in range(a, len(ma_list), len(data.Codes)):
                MA_n[code].append(ma_list[b])
            MA_n[code].reverse()
            a += 1

        # 获取MA_m 和 MA_n 有交点的所有股票代码
        codes = list()
        for code in self.codes:
            for value_m in MA_m[code]:
                for value_n in MA_n[code]:
                    if value_m == value_n:
                        codes.append(code)

        # 排除次新股
        data = c.css(codes, "IPOLSTDAYS", "TradeDate={}".format(getdateformtoday(0)))

        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request css Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    for i in range(0, len(data.Indicators)):
                        if data.Data[code][i] < n:
                            codes.remove(code)
        print("获取简单移动平均数据完毕")
        return codes

    @staticmethod
    def getvalue(codes, m, n):
        Purchase = list()
        Sellout = list()
        if len(codes) != 0:

            MA_mday, close = q.index_ma(codes, m)
            MA_nday, close = q.index_ma(codes, n)

            for code in codes:
                regressioncoefficient = list()
                regr_m = linear_model.LinearRegression()
                X = list()
                for x in range(1, len(MA_mday[code]) + 1):
                    X.append([x])
                regr_m.fit(X, MA_mday[code])
                regressioncoefficient.append(regr_m.coef_)
                regr_n = linear_model.LinearRegression()
                X = list()
                for x in range(1, len(MA_nday[code]) + 1):
                    X.append([x])
                regr_n.fit(X, MA_nday[code])
                regressioncoefficient.append(regr_n.coef_)
                if regressioncoefficient[0] > regressioncoefficient[1]:
                    Purchase.append(code)
                if regressioncoefficient[0] < regressioncoefficient[1]:
                    Sellout.append(code)

        return Purchase, Sellout

    def run(self, m=60, n=30):
        codes = self.getsuitablestock(m, n)
        print("具有交叉点的股票有:" + str(codes))
        Purchase, Sellout = self.getvalue(codes, m, n)
        print("双均线策略选股共选出{}个适合股票购买,为{}".format(len(Purchase), Purchase))
        self.content += "\n双均线策略选股共选出{}个适合股票购买,为{}".format(len(Purchase), Purchase)
        Clearance = list()
        Position = list()
        for account in self.accounts:

            if account in Purchase:
                Purchase.remove(account)

            if account in Sellout:
                Clearance.append(account)

        Position.extend(Purchase[:self.num])
        print("双均线回归策略选股前{}推荐股票为：{}".format(self.num, Position))
        print("根据此策略已有持仓，建议卖出的股票为：{}".format(Clearance))
        self.content += "\n双均线策略选股前{}推荐股票为：{}".format(self.num, Position)
        self.content += "\n根据此策略已有持仓，建议卖出的股票为：{}".format(Clearance)
        print("双均线策略选股以完成")

        # 获取推荐股票的昨收价
        Currentpricelist = list()
        Yieldlist = list()
        for code in Position:
            for price in q.index_close(code, 1).values():
                Currentpricelist.append(price[0])
            for profit in q.index_maavgprofit(code, self.period).values():
                Yieldlist.append(profit[0])

        # 根据收益率算权重（按选定的权重计算周期计算）
        Weightlist = list()
        share = round(1 / sum(range(1, self.num + 1)), 1)
        for value in Yieldlist:
            Weightlist.append(sorted(Yieldlist).index(value) * share)

        # 根据昨收和配额，按权重算出购买股数
        # 剔除某个股股价过高的导致配额不够用的情况

        Numberofshares = 100
        quota = self.quota
        for code in Position:
            if Currentpricelist[Position.index(code)] * Numberofshares >= quota:
                Position.pop(Position.index(code))
                Currentpricelist.pop(Position.index(code))
                print("{}股价过高，超出配额，剔除！".format(code))

        while quota > 0:
            for i in range(0, len(Position)):
                quota -= Currentpricelist[i] * Numberofshares * (1 + Weightlist[i])

            Numberofshares += 100
        data = {}
        data.setdefault('buy', {})
        data.setdefault('sell', {})
        for code in Position:
            data['buy'][code] = [Currentpricelist[Position.index(code)], int(math.ceil(
                Numberofshares * (1 + Weightlist[Position.index(code)]) / 100.0)) * 100
                                 ]
        for code in Clearance:
            data['sell'][code] = '现价平仓'

        data.setdefault('双均线回归策略', str(date.today()))
        if self.Exceloperation.write(data) is True:
            self.content += '\n成功写入今日双均线回归策略策略'
        self.Dataoperation.writetxt(str(self.content), 'Msg/双均线策略.txt')
        return data


class CCIselect:
    """
    CCI指标曲线从下向上突破+100线而进入非常态区间(超买区)，
    当CCI指标曲线从上向下突破-100线而进入另一个非常态区间（超卖区）
    """

    def __init__(self, Dataoperation, Exceloperation, accounts="", commission_ratio=0.0001, N=5, quota=100000,
                 period=7):
        """
        :param Dataoperation: 文件操作类
        :param Exceloperation: EXcel文件操作类
        :param accounts: 已持仓股票东财代码列表（'600031.SH,300059.SZ'）
        :param commission_ratio: 交易费用
        :param N: 需要推荐多少个符合策略的股票
        :param quota: 资金配额
        :param period: 权重计算周期
        """
        self.Dataoperation = Dataoperation
        self.Exceloperation = Exceloperation
        self.codes = sectorCodes()
        self.commission_ratio = commission_ratio
        self.num = N
        self.accounts = accounts
        self.quota = quota
        self.period = period

        print("目前CCI顺势指标策略已持仓：" + str(self.accounts))
        self.content = "目前根据CCI顺势指标策略已持仓：" + str(self.accounts)

    def getvalue(self):
        Risingstock = {}
        Preventstock = {}

        # 获取前一天的CCI指标，用于今天的CCI顺势指标选股
        MACCI = q.index_macci(self.codes, 1)

        for code in self.codes:
            if 100 < MACCI[code][0] < 150:
                Risingstock[code] = MACCI[code]
            else:
                Preventstock[code] = MACCI[code]

        Purchase = list()
        Sellout = list()
        # 从大到小排序
        CCIlist = sorted(list(Risingstock.values()), reverse=True)
        for code, value in MACCI.items():
            if value in CCIlist[:self.num]:
                Purchase.append(code)
        CCIlist = sorted(list(Preventstock.values()), reverse=True)
        for code, value in MACCI.items():
            if value in CCIlist[:self.num]:
                Sellout.append(code)

        return Purchase, Sellout

    def run(self):
        print("开始进行CCI顺势指标策略选股")
        Purchase, Sellout = self.getvalue()
        print("CCI顺势指标策略选股共选出{}个适合股票购买,为{}".format(len(Purchase), Purchase))
        self.content += "\nCCI顺势指标策略选股共选出{}个适合股票购买,为{}".format(len(Purchase), Purchase)

        Clearance = list()
        Position = list()
        for account in self.accounts:

            if account in Purchase:
                Purchase.remove(account)

            if account in Sellout:
                Clearance.append(account)

        Position.extend(Purchase[:self.num])
        print("CCI顺势指标策略选股前{}推荐股票为：{}".format(self.num, Position))
        print("根据此策略已有持仓，建议卖出的股票为：{}".format(Clearance))
        self.content += "\nCCI顺势指标策略选股前{}推荐股票为：{}".format(self.num, Position)
        self.content += "\n根据此策略已有持仓，建议卖出的股票为：{}".format(Clearance)
        print("CCI顺势指标策略选股以完成")

        # 获取推荐股票的昨收价
        Currentpricelist = list()
        Yieldlist = list()
        for code in Position:
            for price in q.index_close(code, 1).values():
                Currentpricelist.append(price[0])
            for profit in q.index_maavgprofit(code, self.period).values():
                Yieldlist.append(profit[0])

        # 根据收益率算权重（按选定的权重计算周期计算）
        Weightlist = list()
        share = round(1 / sum(range(1, self.num + 1)), 1)
        for value in Yieldlist:
            Weightlist.append(sorted(Yieldlist).index(value) * share)

        # 根据昨收和配额，按权重算出购买股数
        # 剔除某个股股价过高的导致配额不够用的情况

        Numberofshares = 100
        quota = self.quota
        for code in Position:
            if Currentpricelist[Position.index(code)] * Numberofshares >= quota:
                Position.pop(Position.index(code))
                Currentpricelist.pop(Position.index(code))
                print("{}股价过高，超出配额，剔除！".format(code))

        while quota > 0:
            for i in range(0, len(Position)):
                quota -= Currentpricelist[i] * Numberofshares * (1 + Weightlist[i])

            Numberofshares += 100
        data = {}
        data.setdefault('buy', {})
        data.setdefault('sell', {})
        for code in Position:
            data['buy'][code] = [Currentpricelist[Position.index(code)], int(math.ceil(
                Numberofshares * (1 + Weightlist[Position.index(code)]) / 100.0)) * 100
                                 ]
        for code in Clearance:
            data['sell'][code] = '现价平仓'

        data.setdefault('CCI顺势指标策略', str(date.today()))
        if self.Exceloperation.write(data) is True:
            self.content += '\n成功写入今日CCI顺势指标策略'
        self.Dataoperation.writetxt(self.content, 'Msg/CCI顺势指标策略.txt')
        return data


class Grid:
    """
    网格交易法是一种利用行情震荡进行获利的策略。在标的价格不断震荡的过程中，
    对标的价格绘制网格，在市场价格触碰到某个网格线时进行加减仓操作尽可能获利。
    """

    def __init__(self, buydata, cmd, RealDataSpider, AlipalSpider, GRIDPOINT=None):
        """
        :param buydata: 需要进行网格买入法操作的购买数据列表[['000006.SZ', 4.44, 400], ['000026.SZ', 11.5, 400]]
        :param cmd:操作命令 'buy' / 'sell'
        :param RealDataSpider:实时数据获取类爬虫
        :param GRIDPOINT:网格[9,8,7,6,5,4,3,2,1]
        :param AlipalSpider: 支付宝模拟炒股爬虫
        """
        codes = list()
        shares = list()
        for data in buydata:
            codes.append(data[0])
            shares.append(data[2])
        self.codes = ','.join(codes)
        self.shares = shares
        self.cmd = cmd
        self.RealDataSpider = RealDataSpider
        self.AlipalSpider = AlipalSpider
        if GRIDPOINT is None:
            self.GRIDPOINT = self.gridpoint(1)
        print("网格点位" + str(self.GRIDPOINT))

        currentprice = self.get_price()
        if self.cmd == 'buy':
            for code, pointlist in self.GRIDPOINT.items():
                for point in pointlist:
                    if point <= currentprice[code]:
                        print("网格交易策略预测{}的第一个买点为{}".format(code, point))
                        break

        if self.cmd == 'sell':
            for code, pointlist in self.GRIDPOINT.items():
                for point in sorted(pointlist):
                    if point >= currentprice[code]:
                        print("网格交易策略预测{}的第一个卖点为{}".format(code, point))
                        break
        print(self.codes)

    def gridpoint(self, N):
        AVPRICE = {}
        Avpricedict = q.index_maavprice(self.codes, N)
        for code, valuelist in Avpricedict.items():
            AVPRICE[code] = np.mean(valuelist)

        SUPPOINT = {}
        PREPOINT = {}
        Supportpointdict, Pressurepointdict = q.stoplossparabola(self.codes, 60)
        for code, suplist in Supportpointdict.items():
            SUPPOINT[code] = [sorted(suplist)[0], sorted(suplist)[1]]
        for code, prelist in Pressurepointdict.items():
            PREPOINT[code] = [sorted(prelist, reverse=True)[0], sorted(prelist, reverse=True)[1]]

        GRIDPOINT = {}
        for code, avprice in AVPRICE.items():
            up = SUPPOINT[code]
            down = PREPOINT[code]
            up.append((up[0] + up[1]) / 2)
            up.append((up[1] + avprice) / 2)
            down.append((down[0] + down[1]) / 2)
            down.append((down[1] + avprice) / 2)
            pointlist = up + down
            pointlist.append(avprice)
            mid_np = np.array(pointlist)
            mid_np_2f = np.round(mid_np, 2)
            GRIDPOINT[code] = sorted(list(mid_np_2f), reverse=True)

        return GRIDPOINT

    def get_price(self):

        data = {}

        stockdata = self.RealDataSpider.run(self.codes, "f43")

        for code in self.codes.split(','):
            data[code] = list()

        for instockdata in stockdata:

            for code, valuedict in instockdata.items():
                data[code].append(valuedict['f43'])

        return data

    def getvalue(self):
        """
        :return: Operationclass:dict类型 , key:东财代码 ，value：价格,操作股数 Operationclass = {‘buy’：‘600031.SH’:[28.21,200]}
        """
        Operationclass = {}
        Operationclass.setdefault(self.cmd, {})

        pricedict = self.get_price()
        # 初始化第一个点位为目前价
        Touchpoint = pricedict

        for code, price in pricedict.items():
            print("{}现价为{}：".format(code, price))
            for point in self.GRIDPOINT[code]:
                if self.cmd == 'buy':
                    if price <= point:
                        if point < Touchpoint[code]:
                            print("触碰到点位：{}".format(Touchpoint[code]))
                            print("以{}价格买入{}".format(price, code))
                            Operationclass['buy'].setdefault(code, [price])
                            Touchpoint[code] = point
                            print("目前触及点位为：{}".format(Touchpoint[code]))

                    else:
                        print("暂无触碰到点位")
                        if point > Touchpoint[code]:
                            # 更新买入点位
                            Touchpoint[code] = point
                            print("更新买入点位：{}".format(point))

                if self.cmd == 'sell':
                    if price >= point:
                        if point > Touchpoint[code]:
                            print("触碰到点位：{}".format(Touchpoint[code]))
                            print("以{}价格卖出{}".format(price, code))
                            Operationclass['buy'].setdefault(code, [price])
                            Touchpoint[code] = point

                    else:
                        print("暂无触碰到点位")
                        if point < Touchpoint[code]:
                            # 更新卖出点位
                            Touchpoint[code] = point
                            print("更新卖出点位：{}".format(point))
                print("+" * 100)

        # 遍历操作数据类：
        if len(Operationclass[self.cmd].keys()) != 0:
            for code in Operationclass[self.cmd].keys():
                # 添加操作股数
                Operationclass[self.cmd][code].append(self.shares[self.codes.split(',').index(code)])
            return Operationclass
        else:
            Operationclass = None
            return Operationclass

    def run(self, seconds):
        print("网格交易策略：")
        Operationclass = self.getvalue()

        if Operationclass is not None:
            self.AlipalSpider.run(Operationclass)

        else:
            print("暂不适合任何交易操作")
        print("等待执行下一次网格交易法，现设定为每{}秒执行一次".format(seconds))
        sleep(seconds)


class Smallmv:
    """
    小市值选股法
    """

    def __init__(self, Dataoperation, Exceloperation, accounts="", commission_ratio=0.0001, N=5, quota=10000,
                 period=7):
        """
        :param Dataoperation: 文件操作类
        :param Exceloperation: EXcel文件操作类
        :param accounts: 已持仓股票东财代码列表（'600031.SH,300059.SZ'）
        :param commission_ratio: 交易费用
        :param N: 需要推荐多少个符合策略的股票
        :param quota: 资金配额
        :param period: 权重计算周期
        """
        self.Dataoperation = Dataoperation
        self.Exceloperation = Exceloperation
        self.codes = sectorCodes()
        self.commission_ratio = commission_ratio
        self.num = N
        self.accounts = accounts
        self.quota = quota
        self.period = period

        print("目前根据小市值选股法策略已持仓：" + str(self.accounts))
        self.content = "目前根据小市值选股法策略已持仓：" + str(self.accounts)

    def getvalue(self):
        MV = {}
        data = c.css(self.codes, "MV", "TradeDate={}".format(getdateformtoday(-1)))
        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request css Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    for i in range(0, len(data.Indicators)):
                        data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                        MV[code] = data.Data[code][i] / 100000000

        Position = {}
        for code in self.codes:
            if 30 < MV[code] < 60:
                Position[code] = MV[code]
        mvlist = sorted(list(Position.values()), reverse=True)
        Purchase = list()
        for code, value in Position.items():
            if value in mvlist:
                Purchase.append(code)

        return Purchase

    def run(self):
        print("开始进行小市值选股策略选股")
        Purchase = self.getvalue()
        print("小市值选股策略选股共选出{}个适合股票购买,为{}".format(len(Purchase), Purchase))
        self.content += "\n小市值选股策略选股共选出{}个适合股票购买,为".format(len(Purchase))
        Position = list()
        Clearance = list()
        for account in self.accounts:
            if account in Purchase:
                Purchase.remove(account)

        Position.extend(Purchase[:self.num])
        print("小市值选股策略选股前{}推荐股票为：{}".format(self.num, Position))
        self.content += "\n小市值选股策略选股前{}推荐股票为：{}".format(self.num, Position)
        print("小市值选股策略选股以完成")

        # 获取推荐股票的昨收价
        Currentpricelist = list()
        Yieldlist = list()
        for code in Position:
            for price in q.index_close(code, 1).values():
                Currentpricelist.append(price[0])
            for profit in q.index_maavgprofit(code, self.period).values():
                Yieldlist.append(profit[0])

        # 根据收益率算权重（按选定的权重计算周期计算）
        Weightlist = list()
        share = round(1 / sum(range(1, self.num + 1)), 1)
        for value in Yieldlist:
            Weightlist.append(sorted(Yieldlist).index(value) * share)

        # 根据昨收和配额，按权重算出购买股数
        # 剔除某个股股价过高的导致配额不够用的情况

        Numberofshares = 100
        quota = self.quota
        for code in Position:
            if Currentpricelist[Position.index(code)] * Numberofshares >= quota:
                Position.pop(Position.index(code))
                Currentpricelist.pop(Position.index(code))
                print("{}股价过高，超出配额，剔除！".format(code))

        while quota > 0:
            for i in range(0, len(Position)):
                quota -= Currentpricelist[i] * Numberofshares * (1 + Weightlist[i])

            Numberofshares += 100
        data = {}
        data.setdefault('buy', {})
        data.setdefault('sell', {})
        for code in Position:
            data['buy'][code] = [Currentpricelist[Position.index(code)], int(math.ceil(
                Numberofshares * (1 + Weightlist[Position.index(code)]) / 100.0)) * 100
                                 ]
        for code in Clearance:
            data['sell'][code] = '现价平仓'

        data.setdefault('小市值选股策略', str(date.today()))

        if self.Exceloperation.write(data) is True:
            self.content += '\n成功写入今日小市值选股策略'
        self.Dataoperation.writetxt(self.content, 'Msg/小市值选股.txt')
        return data


class Overnight:

    def __init__(self, Dataoperation, DailymarketSpider, Exceloperation, accounts="", commission_ratio=0.0001, N=5,
                 quota=100000,
                 period=7):
        """

        :param Dataoperation: 文件操作类
        :param DailymarketSpider:日常数据爬虫
        :param Exceloperation: Excel文件操作类
        :param accounts: 已持仓股票东财代码列表（'600031.SH,300059.SZ'）
        :param commission_ratio: 交易费用
        :param N: 需要推荐多少个符合策略的股票
        :param quota: 资金配额
        :param period: 权重计算周期
        """
        self.Dataoperation = Dataoperation
        self.DailymarketSpider = DailymarketSpider
        self.Exceloperation = Exceloperation
        self.codes = sectorCodes()
        self.commission_ratio = commission_ratio
        self.num = N
        self.accounts = accounts
        self.quota = quota
        self.period = period
        self.content = None

        print("目前根据一夜持股策略已持仓：" + str(self.accounts))
        self.content = "目前根据一夜持股策略已持仓：" + str(self.accounts)

    def getvalue(self):
        Fluctuationrange = {}
        Volumeratio = {}
        Turnoverrate = {}
        Marketvalue = {}

        print("开始获取一夜持股策略所需判断数据")
        latestprice, fluctuationrange, high, low, start, volumeratio, turnoverrate, marketvalue, codes = self.DailymarketSpider.run()
        for code in codes:

            if 3 <= round(float(fluctuationrange[code])) <= 5:
                Fluctuationrange[code] = fluctuationrange[code]
            if volumeratio[code] != '"-"':
                if 1.5 <= round(float(volumeratio[code])) <= 2.5:
                    Volumeratio[code] = volumeratio[code]

            if 5 <= round(float(turnoverrate[code])) <= 10:
                Turnoverrate[code] = turnoverrate[code]

            if 50 <= round(float(marketvalue[code])) / 100000000 <= 200:
                Marketvalue[code] = marketvalue[code]
        Recommendedbuy = {}
        for code in Fluctuationrange.keys() & Volumeratio.keys() & Turnoverrate.keys() & Marketvalue.keys():
            Recommendedbuy[code] = abs(1 - float(Fluctuationrange[code]) / np.mean(
                list(map(float, list(Fluctuationrange.values()))))) + abs(
                1 - float(Volumeratio[code]) / np.mean(list(map(float, list(Volumeratio.values()))))) + abs(
                1 - float(Turnoverrate[code]) / np.mean(list(map(float, list(Turnoverrate.values()))))) + abs(
                1 - float(Marketvalue[code]) / np.mean(list(map(float, list(Marketvalue.values())))))
        Purchase = list()
        scorelist = sorted(list(Recommendedbuy.values()))
        for score in scorelist:
            for code, value in Recommendedbuy.items():
                if value == score:
                    Purchase.append(code)

        for Crawlercode in Purchase:
            for Dongcaicode in self.codes:
                # 处理东财代码 （000001.SZ）  爬虫返回的代码为301071
                if Crawlercode.replace('"', '') == Dongcaicode.split('.')[0]:
                    Purchase[Purchase.index(Crawlercode)] = Dongcaicode
        return Purchase

    def run(self):
        print("开始进行一夜持股策略选股")
        Purchase = self.getvalue()
        print("一夜持股策略选股共选出{}个适合股票购买,为{}".format(len(Purchase), Purchase))
        self.content += "\n一夜持股策略选股共选出{}个适合股票购买,为:".format(len(Purchase)) + str(Purchase)

        Position = list()
        Clearance = list()
        for account in self.accounts:

            if account in Purchase:
                Purchase.remove(account)

        Position.extend(Purchase[:self.num])
        print("一夜持股策略选股前{}推荐股票为：{}".format(self.num, Position))

        self.content += "\n一夜持股策略选股前{}推荐股票为：".format(self.num) + str(Position)

        print("一夜持股策略选股以完成")

        # 获取推荐股票的昨收价
        Currentpricelist = list()
        Yieldlist = list()
        for code in Position:
            for price in q.index_close(code, 1).values():
                Currentpricelist.append(price[0])
            for profit in q.index_maavgprofit(code, self.period).values():
                Yieldlist.append(profit[0])

        # 根据收益率算权重（按选定的权重计算周期计算）
        Weightlist = list()
        share = round(1 / sum(range(1, self.num + 1)), 1)
        for value in Yieldlist:
            Weightlist.append(sorted(Yieldlist).index(value) * share)

        # 根据昨收和配额，按权重算出购买股数
        # 剔除某个股股价过高的导致配额不够用的情况

        Numberofshares = 100
        quota = self.quota
        for code in Position:
            if Currentpricelist[Position.index(code)] * Numberofshares >= quota:
                Position.pop(Position.index(code))
                Currentpricelist.pop(Position.index(code))
                print("{}股价过高，超出配额，剔除！".format(code))

        while quota > 0:
            for i in range(0, len(Position)):
                quota -= Currentpricelist[i] * Numberofshares * (1 + Weightlist[i])

            Numberofshares += 100
        data = {}
        data.setdefault('buy', {})
        data.setdefault('sell', {})
        for code in Position:
            data['buy'][code] = [Currentpricelist[Position.index(code)], int(math.ceil(
                Numberofshares * (1 + Weightlist[Position.index(code)]) / 100.0)) * 100
                                 ]
        for code in Clearance:
            data['sell'][code] = '现价平仓'

        data.setdefault('一夜持股法策略', str(date.today()))
        if self.Exceloperation.write(data) is True:
            self.content += '\n成功写入今日一夜持股法策略'
        self.Dataoperation.writetxt(self.content, 'Msg/一夜持股策略.txt')
        return data


class MACD_KDJ:

    def __init__(self, buydata, cmd, RealDataSpider, AlipalSpider):
        """
        :param buydata: 需要进行网格买入法操作的购买数据列表[['000006.SZ', 4.44, 400], ['000026.SZ', 11.5, 400]]
        :param cmd:操作命令 'buy' / 'sell'
        :param RealDataSpider:实时数据获取类爬虫
        :param AlipalSpider: 支付宝模拟炒股爬虫
        """
        codes = list()
        shares = list()
        for data in buydata:
            codes.append(data[0])
            shares.append(data[2])
        self.codes = ','.join(codes)
        self.shares = shares
        self.cmd = cmd
        self.RealDataSpider = RealDataSpider
        self.AlipalSpider = AlipalSpider
        self.Nminprice = {}
        self._KDJ = {}
        self._MACD = {}
        for code in self.codes.split(','):
            self.Nminprice[code] = list()
            self._MACD[code] = [0, 0]
            self._KDJ[code] = [0, 0, 0]

    @staticmethod
    def EMA(arr):
        df = pd.DataFrame(arr)
        return df.ewm(span=len(arr), min_periods=len(arr)).mean().values[-1]

    def CalculateMACD(self, pricelist, _DEA):
        MACD = list()
        EMA_12 = int(self.EMA(pricelist[:12]).flat[-1])

        EMA_26 = int(self.EMA(pricelist[12:26]).flat[-1])

        DIF = EMA_12 - EMA_26
        MACD.append(DIF)
        DEA = _DEA * 8 / 10 + DIF * 2 / 10
        MACD.append(DEA)
        BAR = 2 * (DIF - DEA)
        MACD.append(BAR)

        return MACD

    @staticmethod
    def CalculateKAJ(pricelist, _KDJ):
        KDJ = list()
        RSV = 0
        if max(pricelist) - min(pricelist) != 0:
            RSV = (pricelist[-1] - min(pricelist)) / (max(pricelist) - min(pricelist)) * 100
        K = 2 / 3 * _KDJ[0] + 1 / 3 * RSV
        KDJ.append(K)
        D = 2 / 3 * _KDJ[1] + 1 / 3 * K
        KDJ.append(D)
        J = 3 * K - 2 * D
        KDJ.append(J)

        return KDJ

    @staticmethod
    def Calculatetrend(pricelist):
        regr = linear_model.LinearRegression()
        X = list()
        for x in range(1, len(pricelist) + 1):
            X.append([x])
        regr.fit(X, pricelist)
        return round((regr.coef_.tolist()[0]), 2)

    def get_price(self):

        data = {}

        stockdata = self.RealDataSpider.run(self.codes, "f43")

        for code in self.codes.split(','):
            data[code] = list()

        for instockdata in stockdata:

            for code, valuedict in instockdata.items():
                if valuedict['f43'] == '-':
                    valuedict['f43'] = 0
                data[code].append(valuedict['f43'])

        return data

    def getvalue(self):
        """
        :return: Operationclass:dict类型 , key:东财代码 ，value：价格,操作股数 Operationclass = {‘buy’：‘600031.SH’:[28.21,200]}
        """
        Operationclass = {}
        Operationclass.setdefault(self.cmd, {})

        # 获取数据，并加以判断、显示和更新
        data = self.get_price()
        KDJ = {}
        MACD = {}
        for code, price in data.items():
            self.Nminprice[code].extend(price)
            if len(self.Nminprice[code]) >= 26:
                MACD[code] = self.CalculateMACD(self.Nminprice[code], _DEA=self._MACD[code][1])
                KDJ[code] = self.CalculateKAJ(self.Nminprice[code], _KDJ=self._KDJ[code])
                self.Nminprice[code].pop(-1)

                # 处理买入卖出事件
                # 处理买事件：
                if self.cmd == 'buy':
                    # 当K值小于20 ， D值小于20
                    if KDJ[code][0] <= 20 and KDJ[code][1] <= 20:
                        # K值或者D值大于上一次数据，即K值或者D值开始反转增大的情况下，价格下跌见底，可以着手买入
                        if KDJ[code][0] > self._KDJ[code][0] or KDJ[code][1] > self._KDJ[code][1]:
                            if code not in Operationclass['buy'].keys():
                                Operationclass['buy'].setdefault(code, [price])
                            print("以{}价买入{}".format(price, code))

                    # 等待判断完成，更新过去时间段的KDJ
                    self._KDJ[code] = KDJ[code]

                    # 当上次数据DIF小于DEA，即DIF线在DEA线下方
                    if self._MACD[code][0] < self._MACD[code][1]:
                        # 当DIF大于等于DEA，即DIF从下方向上与DEA产生交点，俗称金叉时，可以着手买入
                        if MACD[code][0] >= MACD[code][1]:
                            if code not in Operationclass['buy'].keys():
                                Operationclass['buy'].setdefault(code, [price])
                            print("以{}价买入{}".format(price, code))

                    # 等待判断完成，更新过去时间段的MACD
                    self._MACD[code] = MACD[code]

                # 处理卖事件：
                if self.cmd == 'sell':
                    # 当K值大于80,或者D值大于80，上涨动能不足
                    if KDJ[code][0] >= 80 or KDJ[code][1] >= 80:
                        # K值或者D值小于上一次数据，即K值或者D值开始反转减小的情况下，价格上涨见顶，可以着手卖出
                        if KDJ[code][0] < self._KDJ[code][0] or KDJ[code][1] < self._KDJ[code][1]:
                            if code not in Operationclass['sell'].keys():
                                Operationclass['sell'].setdefault(code, [price])
                            print("以{}价卖出{}".format(price, code))

                    # 等待判断完成，更新过去时间段的KDJ
                    self._KDJ[code] = KDJ[code]

                    # 当上次数据DIF大于DEA，即DIF线在DEA线上方
                    if self._MACD[code][0] > self._MACD[code][1]:
                        # 当DIF小于等于DEA，即DIF从上方向下与DEA产生交点，俗称死叉时，可以着手卖出
                        if MACD[code][0] <= MACD[code][1]:
                            if code not in Operationclass['sell'].keys():
                                Operationclass['sell'].setdefault(code, [price])
                            print("以{}价卖出{}".format(price, code))

                    # 等待判断完成，更新过去时间段的MACD
                    self._MACD[code] = MACD[code]
            # 输出信息
            print("过去25分钟内{}股价：".format(code) + str(self.Nminprice[code]))
            print("{}过去25分钟价格趋势系数为".format(code) + str(self.Calculatetrend(self.Nminprice[code])))
            print("{}现价：".format(code) + str(data[code]) + "均价为：" + str(
                round(float(np.mean(self.Nminprice[code])), 2)))
            if code in KDJ.keys() and code in MACD.keys():
                print("{}现时MACD/KDJ：".format(code) + str(MACD[code]) + str(KDJ[code]))
            else:
                print("{}暂无获取并计算到MACD/KDJ".format(code))
            print("=" * 100)
        # 遍历操作数据类：
        if len(Operationclass[self.cmd].keys()) != 0:
            for code in Operationclass[self.cmd].keys():
                # 添加操作股数
                Operationclass[self.cmd][code].append(self.shares[self.codes.split(',').index(code)])
            return Operationclass
        else:
            Operationclass = None
            return Operationclass

    def run(self, seconds):
        print("macd叠加kdj策略：")
        Operationclass = self.getvalue()

        if Operationclass is not None:
            self.AlipalSpider.run(Operationclass)

        else:
            print("暂不适合任何交易操作")
        print("等待执行下一次MACD叠加KDJ交易法，现设定为每{}秒执行一次".format(seconds))
        sleep(seconds)
