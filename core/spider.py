# -*- coding:utf-8 -*-

from datetime import datetime
from requests import get, ConnectionError
from json import loads
from re import compile, S
from threading import Thread


class RealDataSpider:
    def __init__(self):
        self.GS_API = 'http://push2.eastmoney.com/api/qt/stock/get'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/93.0.4577.82 Safari/537.36"}

        self.datatype = {'f43': '最新价', 'f44': '最高', 'f45': '最低', 'f46': '今开', 'f47': '成交量', 'f48': '成交额',
                         'f50': '量比',
                         'f51': '涨停', 'f52': '跌停', 'f55': '收益', 'f57': '代码', 'f58': '名称', 'f60': '昨收', 'f71': '均价',
                         'f92': '美股净资产', 'f105': '净利润', 'f116': '总市值', 'f117': '流通市值', 'f162': '市盈动',
                         'f167': '市净', 'f168': '换手', 'f169': '涨跌', 'f170': '涨幅', 'f173': 'ROE', 'f183': '总营收',
                         'f186': '毛利率', 'f187': '净利率',
                         'f188': '负债率', 'f191': '委比', 'f192': '委差', 'f193': '主力净比', 'f194': '超大单净比', 'f195': '大单净比',
                         'f196': '中单净比', 'f197': '小单净比', }
        self.parameters = 'f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f60,f71,f92,f105,f116,f117,f162,f167,f168,' \
                          'f169,f170,f173,f183,f186,f187,f188,f191,f192,f193,f194,f195,f196,f197 '

    def get_url(self, codes, parameters):
        if parameters != 'default':
            self.parameters = parameters
        params_dict = {}
        for i in range(0, int(len(codes.replace(',', '')) / 9)):
            code = codes[10 * i:10 * i + 9]

            if code[-2:] == "SH":
                params = {
                    'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                    'invt': '2',
                    'fltt': '2',
                    'fields': self.parameters,
                    'secid': '%s.%s' % (1, code[:6]),
                    'cb': 'jQuery112405831440079032297_1578892365285',
                    '_': '1578892365407'
                }
                params_dict[code] = params

            if code[-2:] == "SZ":
                params = {
                    'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                    'invt': '2',
                    'fltt': '2',
                    'fields': self.parameters,
                    'secid': '%s.%s' % (0, code[:6]),
                    'cb': 'jQuery112405831440079032297_1578892365285',
                    '_': '1578892365407'
                }
                params_dict[code] = params

        return params_dict

    def parse_url(self, params):
        """获取网页源码"""
        try:
            response = get(self.GS_API, params=params, headers=self.headers, timeout=5)
            print("爬取：" + str(response.url))
            if response.status_code == 200:
                return response.text
        except ConnectionError as e:
            print('Error', e.args)

    def get_stockdata(self, code, content):
        stockdata = {code: {}}
        content = content.replace("jQuery112405831440079032297_1578892365285", '').replace('(', "").replace(')',
                                                                                                            '').replace(
            ';', '')

        if loads(content) is not None:
            for parameter in self.parameters.split(','):
                data = loads(content)['data'][parameter]
                stockdata[code].setdefault(parameter, data)
            return stockdata

    def save_stockdata(self, stockdata):

        for code, datadict in stockdata.items():
            for parameter, data in datadict.items():
                for datatype, zhname in self.datatype.items():
                    if parameter == datatype:
                        parameter = zhname
                        # stockdata[code][zhname] = stockdata[code].pop(parameter)
                con = "[%s] [%s] [%s]: %s。" % (code, datetime.now(), parameter, data)
                print(con)
        return stockdata

    def run(self, codes, parameters='default'):

        Data_list = list()
        gpurl_dict = self.get_url(codes, parameters=parameters)
        for code, url in gpurl_dict.items():

            content = self.parse_url(url)
            stockdata = self.get_stockdata(code, content)

            if stockdata is not None:
                Data_list.append(stockdata)

        return Data_list


class DailymarketSpider:
    def __init__(self):
        self.url = 'http://76.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112408744624686429123_1578798932591&pn={} \
                   &pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:' \
                   '0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,' \
                   'f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_=1586266306109'

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"}

    def get_url(self):

        url_list = list()
        Pagenumber = None

        content = self.parse_url(self.url.format(1))

        """re选择数据中的total"""
        pattern = compile('"total":(?P<Total>.+?),.*?', S)
        result = pattern.finditer(content)

        for value in result:
            Pagenumber = round(int(value.groups()[0]) / 20 + 1)

        """构建url列表"""
        for pn in range(1, Pagenumber):
            url_list.append(self.url.format(pn))

        return url_list

    def parse_url(self, url):
        """获取网页源码"""
        try:
            response = get(url, headers=self.headers)
            if response.status_code == 200:
                print("爬取：" + str(response.url))
                return response.text
        except ConnectionError as e:
            print('Error', e.args)

    @staticmethod
    def get_stockdata(content):
        """获取股票代码、名称、PE"""
        com = compile(
            '"f2":(?P<Latestprice>.+?),.*?"f3":(?P<Fluctuationrange>.+?),.*?"f8":(?P<Turnoverrate>.+?),.*?"f10":('
            '?P<Volumeratio>.+?),.*?"f12":(?P<Code>.+?),.*?"f15":(?P<High>.+?),.*?"f16":(?P<Low>.+?),'
            '.*?"f17":(?P<Open>.+?),.*?"f20":(?P<Marketvalue>.+?),',
            S)
        ret = com.finditer(content)
        for i in ret:
            yield {
                'Code': i.group('Code'),
                'Turnoverrate': i.group('Turnoverrate'),
                'Latestprice': i.group('Latestprice'),
                'Fluctuationrange': i.group('Fluctuationrange'),
                'High': i.group('High'),
                'Low': i.group('Low'),
                'Open': i.group('Open'),
                'Volumeratio': i.group('Volumeratio'),
                'Marketvalue': i.group('Marketvalue')
            }

    @staticmethod
    def save_stockdata(data):
        Latestprice = {}
        Fluctuationrange = {}
        High = {}
        Low = {}
        Open = {}
        Volumeratio = {}
        Turnoverrate = {}
        Marketvalue = {}
        codes = list()
        for category in data:  # 每一页的数据
            code = category.get('Code')
            turnoverrate = category.get('Turnoverrate')
            latestprice = category.get('Latestprice')
            fluctuationrange = category.get('Fluctuationrange')
            high = category.get('High')
            low = category.get('Low')
            start = category.get('Open')
            volumeratio = category.get('Volumeratio')
            marketvalue = category.get('Marketvalue')
            if start == '"-"':
                continue
            else:
                Latestprice[code] = latestprice
                Fluctuationrange[code] = fluctuationrange
                High[code] = high
                Low[code] = low
                Open[code] = open
                Volumeratio[code] = volumeratio
                Turnoverrate[code] = turnoverrate
                Marketvalue[code] = marketvalue
                codes.append(code)

        return Latestprice, Fluctuationrange, High, Low, Open, Volumeratio, Turnoverrate, Marketvalue, codes

    def run(self):
        print("开始获取日常数据")
        Latestprice = {}
        Fluctuationrange = {}
        High = {}
        Low = {}
        Open = {}
        Volumeratio = {}
        Turnoverrate = {}
        Marketvalue = {}
        codes = list()
        url_list = self.get_url()

        for url in url_list:
            content = self.parse_url(url)
            data = self.get_stockdata(content)
            ReLatestprice, ReFluctuationrange, ReHigh, ReLow, ReOpen, ReVolumeratio, ReTurnoverrate, Remarketvalue, ReCodes = self.save_stockdata(
                data)  # 每一页的数据
            Latestprice.update(ReLatestprice)
            Fluctuationrange.update(ReFluctuationrange)
            High.update(ReHigh)
            Low.update(ReLow)
            Open.update(ReOpen)
            Volumeratio.update(ReVolumeratio)
            Turnoverrate.update(ReTurnoverrate)
            Marketvalue.update(Remarketvalue)
            codes.extend(ReCodes)

        return Latestprice, Fluctuationrange, High, Low, Open, Volumeratio, Turnoverrate, Marketvalue, codes


class PalSpider:
    def __init__(self, BotsendMsg):
        """
        :param BotsendMsg:
        """
        self.BotsendMsg = BotsendMsg

    def get_url(self):
        pass

    def parse_url(self, url):
        pass

    # 操作交易函数
    def operationaltransaction(self, Operationclass):
        if list(Operationclass.keys()) == ['buy']:
            for code, data in Operationclass['buy'].items():
                self.BotsendMsg.send_msg_txt("以{}价格挂出{}买单{}股".format(data[0], code, data[1]))
                # 用字典记录买入已实现dict = {‘buy’:{‘600031.SH':[price,shares]},'time':datetime.now().strftime('%m-%d-%H-%M')}
        if list(Operationclass.keys()) == ['sell']:
            for code, data in Operationclass['sell'].items():
                self.BotsendMsg.send_msg_txt("以{}价格挂出{}卖单{}股".format(data[0], code, data[1]))
                # 用字典记录卖出已实现dict = {‘buy’:{‘600031.SH':[price,shares]},'time':datetime.now().strftime('%m-%d-%H-%M')}

    def run(self, Operationclass):

        t = Thread(target=self.operationaltransaction, args=[Operationclass])
        t.start()
        # 可有可无的阻塞
        # t.join()
