# -*- coding:utf-8 -*-
__author__ = 'linxinloningg'

from EmQuantAPI import *


class q:
    def __init__(self):
        pass

    @classmethod
    def index_maarbp(cls, codes, N):
        """
        人气意愿指标移动函数
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:人气意愿指标字典 ，key:股票代码，value：指标数值
        """
        MAARBP = {}
        maarbp_list = list()
        data = None
        for n in range(0, N):
            data = c.css(codes, "ARBP", "TradeDate={},N=26,ArBr=1,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            maarbp_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            MAARBP[code] = list()
            for b in range(a, len(maarbp_list), len(data.Codes)):
                MAARBP[code].append(maarbp_list[b])
            a += 1
        return MAARBP

    @classmethod
    def index_maavgprofit(cls, codes, N):
        """
        平均收益移动函数
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:平均收益字典 ，key:股票代码，value：平均收益数值
        """
        MAAVG = {}
        maavg_list = list()

        data = c.css(codes, "AVGRETURN",
                     "StartDate={},EndDate={},ComputingCycle=2,CalcType=1".format(getdateformtoday(-N),
                                                                                  getdateformtoday(0)))
        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request css Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    for i in range(0, len(data.Indicators)):
                        data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                        maavg_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            MAAVG[code] = list()
            for b in range(a, len(maavg_list), len(data.Codes)):
                MAAVG[code].append(maavg_list[b])
            a += 1
        return MAAVG

    @classmethod
    def index_maavprice(cls, codes, N):
        """
        平均价格移动函数
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:平均价格字典 ，key:股票代码，value：平均价格数值
        """
        AVPRICE = {}
        avprice_list = list()
        data = c.csd(codes, "AVERAGE", getdateformtoday(-N), getdateformtoday(0),
                     "period=1,adjustflag=1,curtype=1,order=1,market=CNSESH")
        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request csd Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    for i in range(0, len(data.Indicators)):
                        for j in range(0, len(data.Dates)):
                            data.Data[code][i][j] = 0 if data.Data[code][i][j] is None else data.Data[code][i][j]
                            avprice_list.append(data.Data[code][i][j])
        a = 0
        for code in data.Codes:
            AVPRICE[code] = list()
            for b in range(a, len(avprice_list), len(data.Codes)):
                AVPRICE[code].append(avprice_list[b])
            a += 1
        return AVPRICE

    @classmethod
    def index_mabias(cls, codes, N):
        """
        乖离率移动函数
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:乖离率指标字典 ，key:股票代码，value：乖离率指标数值
        """
        MABIAS = {}
        mabias_list = list()
        data = None
        for n in range(0, N):
            data = c.css(codes, "BIAS", "TradeDate={},N={},AdjustFlag=1,Period=1".format(getdateformtoday(-n), N))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            mabias_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            MABIAS[code] = list()
            for b in range(a, len(mabias_list), len(data.Codes)):
                MABIAS[code].append(mabias_list[b])
            a += 1
        return MABIAS

    @classmethod
    def index_boll(cls, codes, N):
        """
        布林线移动函数
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:MAMID：中轨；MAUPPER：上轨，MALOWER：下轨，key:股票代码，value：指标数值
        """
        MAMID = {}
        mamid_list = list()
        data = None
        for n in range(0, N):
            data = c.css(codes, "BOLL",
                         "TradeDate={},N=20,K=2,Boll=1,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            mamid_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            MAMID[code] = list()
            for b in range(a, len(mamid_list), len(data.Codes)):
                MAMID[code].append(mamid_list[b])
            MAMID[code].reverse()
            a += 1
        MAUPPER = {}
        maupper_list = list()

        for n in range(0, N):
            data = c.css(codes, "BOLL",
                         "TradeDate={},N=20,K=2,Boll=2,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            maupper_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            MAUPPER[code] = list()
            for b in range(a, len(maupper_list), len(data.Codes)):
                MAUPPER[code].append(maupper_list[b])
            MAUPPER[code].reverse()
            a += 1
        MALOWER = {}
        malower_list = list()
        for n in range(0, N):
            data = c.css(codes, "BOLL",
                         "TradeDate={},N=20,K=2,Boll=3,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            malower_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            MALOWER[code] = list()
            for b in range(a, len(malower_list), len(data.Codes)):
                MALOWER[code].append(malower_list[b])
            MALOWER[code].reverse()
            a += 1
        return MAMID, MAUPPER, MALOWER

    @classmethod
    def index_macci(cls, codes, N):
        """
        CCI顺势指标移动函数
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:CCI顺势指标字典 ，key:股票代码，value：指标数值
        """
        MACCI = {}
        macci_list = list()
        data = None
        for n in range(0, N):
            data = c.css(codes, "CCI", "TradeDate={},N=14,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            macci_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            MACCI[code] = list()
            for b in range(a, len(macci_list), len(data.Codes)):
                MACCI[code].append(macci_list[b])
            a += 1
        return MACCI

    @classmethod
    def index_macr(cls, codes, N):
        """
        CR能量指标
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:CR能量指标字典 ，key:股票代码，value：指标数值
        """
        MACR = {}
        macr_list = list()
        data = None
        for n in range(0, N):
            data = c.css(codes, "OBV", "TradeDate={},Obv=1,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            macr_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            MACR[code] = list()
            for b in range(a, len(macr_list), len(data.Codes)):
                MACR[code].append(macr_list[b])
            a += 1
        return MACR

    @classmethod
    def index_madma(cls, codes, N):
        """
        平行线差（DMA）指标
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:DMA:股价短期平均值—股价长期平均值,AMA:DMA短期平均值 ，key:股票代码，value：指标数值
        """
        DMA = {}
        dma_list = list()
        data = None
        for n in range(0, N):
            data = c.css(codes, "DMA",
                         "TradeDate={},N1=10,N2=50,N3=10,Dma=1,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            dma_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            DMA[code] = list()
            for b in range(a, len(dma_list), len(data.Codes)):
                DMA[code].append(dma_list[b])
            DMA[code].reverse()
            a += 1
        AMA = {}
        ama_list = list()
        for n in range(0, N):
            data = c.css(codes, "DMA",
                         "TradeDate={},N1=10,N2=50,N3=10,Dma=2,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            ama_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            AMA[code] = list()
            for b in range(a, len(ama_list), len(data.Codes)):
                AMA[code].append(ama_list[b])
            AMA[code].reverse()
            a += 1
        return DMA, AMA

    @classmethod
    def index_dmi(cls, codes, N):
        """
        动向指标或趋向指标
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:
        +DI（即PDI，下同)、-DI（即MDI，下同)、ADX、ADXR,
        多空指标(+DI、-DI)和趋向指标(ADX、ADXR)两组指标
         key:股票代码，value：指标数值
        """
        UPDI = {}
        updi_list = list()
        data = None
        for n in range(0, N):
            data = c.css(codes, "DMI",
                         "TradeDate={},N=14,N1=6,Dmi=1,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            updi_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            UPDI[code] = list()
            for b in range(a, len(updi_list), len(data.Codes)):
                UPDI[code].append(updi_list[b])
            UPDI[code].reverse()
            a += 1

        LOWDI = {}
        lowdi_list = list()
        for n in range(0, N):
            data = c.css(codes, "DMI",
                         "TradeDate={},N=14,N1=6,Dmi=2,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            lowdi_list.append(data.Data[code][i])

        a = 0
        for code in data.Codes:
            LOWDI[code] = list()
            for b in range(a, len(lowdi_list), len(data.Codes)):
                LOWDI[code].append(lowdi_list[b])
            LOWDI[code].reverse()
            a += 1

        ADX = {}
        adx_list = list()
        for n in range(0, N):
            data = c.css(codes, "DMI",
                         "TradeDate={},N=14,N1=6,Dmi=3,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            adx_list.append(data.Data[code][i])

        a = 0
        for code in data.Codes:
            ADX[code] = list()
            for b in range(a, len(adx_list), len(data.Codes)):
                ADX[code].append(adx_list[b])
            ADX[code].reverse()
            a += 1

        ADXR = {}
        adxr_list = list()
        for n in range(0, N):
            data = c.css(codes, "DMI",
                         "TradeDate={},N=14,N1=6,Dmi=4,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            adxr_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            ADXR[code] = list()
            for b in range(a, len(adxr_list), len(data.Codes)):
                ADXR[code].append(adxr_list[b])
            ADXR[code].reverse()
            a += 1
        return UPDI, LOWDI, ADX, ADXR

    @classmethod
    def index_maemv(cls, codes):
        """
        简单波段指标
        :param codes:东财代码
        :return:25天简单波段指标字典 ，key:股票代码，value：指标数值
        """
        EMVA = {}
        data = c.csd(codes, "HIGH,LOW,AMOUNT", getdateformtoday(-14 - 9), getdateformtoday(0),
                     "period=1,adjustflag=1,curtype=1,order=1,market=CNSESH")
        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request csd Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    emva = list()
                    data_list = list()
                    for i in range(0, len(data.Indicators)):
                        for j in range(0, len(data.Dates)):
                            data.Data[code][i][j] = 0 if data.Data[code][i][j] is None else data.Data[code][i][j]
                            data_list.append(data.Data[code][i][j])

                    for n in range(0, 9):
                        emv = 0
                        for i in range(n, 14 + n):
                            emv += ((data_list[i] + data_list[i + 15]) / 2 - (
                                    data_list[i + 1] + data_list[i + 16]) / 2) * (
                                           data_list[i + 1] - data_list[i + 16]) / data_list[i + 31]
                        emva.append(round(emv, 3))

                    EMVA[code] = list(reversed(emva))

                return EMVA

    @classmethod
    def index_maenv(cls, codes, N):
        """
        价格波动范围指标
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:价格波动范围指标（上、中、下三条线）字典 ，key:股票代码，value：指标数值
        """
        MAUPENV = {}
        maupenv_list = list()
        MALOWENV = {}
        malowenv_list = list()
        for n in range(0, N):
            data = c.css(codes, "ENV",
                         "TradeDate={},N=14,Env=1,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            maupenv_list.append(data.Data[code][i])
            data = c.css(codes, "ENV",
                         "TradeDate={},N=14,Env=2,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            malowenv_list.append(data.Data[code][i])
        CLOSE = {}
        close_list = list()
        data = c.csd(codes, "CLOSE", getdateformtoday(-N + 1), getdateformtoday(0),
                     "period=1,adjustflag=1,curtype=1,order=1,market=CNSESH")
        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request csd Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    for i in range(0, len(data.Indicators)):
                        for j in range(0, len(data.Dates)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            close_list.append(data.Data[code][i][j])
        a = 0
        for code in data.Codes:
            MAUPENV[code] = list()
            for b in range(a, len(maupenv_list), len(data.Codes)):
                MAUPENV[code].append(maupenv_list[b])
            MAUPENV[code].reverse()
            a += 1
        a = 0
        for code in data.Codes:
            MALOWENV[code] = list()
            for b in range(a, len(malowenv_list), len(data.Codes)):
                MALOWENV[code].append(malowenv_list[b])
            MALOWENV[code].reverse()
            a += 1
        a = 0
        for code in data.Codes:
            CLOSE[code] = list()
            CLOSE[code].extend(close_list[a * N:(a + 1) * N])
            a += 1
        return MAUPENV, MALOWENV, CLOSE

    @classmethod
    def index_kdj(cls, codes, N):
        """
        kdj随机指标
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:K值、D值与J值
        """
        K = {}
        k_list = list()
        data = None
        for n in range(0, N):
            data = c.css(codes, "KDJ",
                         "TradeDate={},N=9,N1=3,N2=3,Kdj=1,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            k_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            K[code] = list()
            for b in range(a, len(k_list), len(data.Codes)):
                K[code].append(k_list[b])
            K[code].reverse()
            a += 1
        D = {}
        d_list = list()
        for n in range(0, N):
            data = c.css(codes, "KDJ",
                         "TradeDate={},N=9,N1=3,N2=3,Kdj=2,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            d_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            D[code] = list()
            for b in range(a, len(d_list), len(data.Codes)):
                D[code].append(d_list[b])
            D[code].reverse()
            a += 1
        J = {}
        j_list = list()
        for n in range(0, N):
            data = c.css(codes, "KDJ",
                         "TradeDate={},N=9,N1=3,N2=3,Kdj=3,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            j_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            J[code] = list()
            for b in range(a, len(j_list), len(data.Codes)):
                J[code].append(j_list[b])
            J[code].reverse()
            a += 1
        return K, D, J

    @classmethod
    def index_ma(cls, codes, N):
        """
        MA简单移动平均
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:MA简单移动平均指标字典 ，key:股票代码，value：指标数值
        """
        MA = {}
        ma_list = list()
        for n in range(0, N):
            data = c.css(codes, "MA",
                         "TradeDate={},N={},K=3,Boll=1,AdjustFlag=1,Period=1".format(getdateformtoday(-n), N))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            ma_list.append(data.Data[code][i])
        CLOSE = {}
        close_list = list()
        data = c.csd(codes, "CLOSE", getdateformtoday(-N + 1), getdateformtoday(0),
                     "period=1,adjustflag=1,curtype=1,order=1,market=CNSESH")
        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request csd Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    for i in range(0, len(data.Indicators)):
                        for j in range(0, len(data.Dates)):
                            data.Data[code][i][j] = 0 if data.Data[code][i][j] is None else data.Data[code][i][j]
                            close_list.append(data.Data[code][i][j])
        a = 0
        for code in data.Codes:
            MA[code] = list()
            for b in range(a, len(ma_list), len(data.Codes)):
                MA[code].append(ma_list[b])
            MA[code].reverse()
            a += 1
        a = 0
        for code in data.Codes:
            CLOSE[code] = list()
            CLOSE[code].extend(close_list[a * N:(a + 1) * N])
            a += 1
        return MA, CLOSE

    @classmethod
    def index_macd(cls, codes, N):
        """
        MACD指数平滑异同平均
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:MACD指数平滑异同平均指标字典 ，离差值（DIF）,平滑移动平均线DEA（也叫MACD、DEM）线,key:股票代码，value：指标数值
        """
        DIFF = {}
        diff_list = list()
        data = None
        for n in range(0, N):
            data = c.css(codes, "MACD",
                         "TradeDate={},N1=12,N2=26,N3=9,Macd=1,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            diff_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            DIFF[code] = list()
            for b in range(a, len(diff_list), len(data.Codes)):
                DIFF[code].append(diff_list[b])
            DIFF[code].reverse()
            a += 1
        DEA = {}
        dea_list = list()
        for n in range(0, N):
            data = c.css(codes, "MACD",
                         "TradeDate={},N1=12,N2=26,N3=9,Macd=2,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            dea_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            DEA[code] = list()
            for b in range(a, len(dea_list), len(data.Codes)):
                DEA[code].append(dea_list[b])
            DEA[code].reverse()
            a += 1

        return DIFF, DEA

    @classmethod
    def index_maobv(cls, codes, N):
        """
        能量潮指标，能量潮是将成交量数量化，制成趋势线，配合股价趋势线，从价格的变动及成交量的增减关系
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:能量潮指标指标字典 ，key:股票代码，value：指标数值
        """
        MAOBV = {}
        maobv_list = list()
        data = None
        for n in range(0, N):

            data = c.css(codes, "OBV", "TradeDate={},Obv=1,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))

            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            maobv_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            MAOBV[code] = list()
            for b in range(a, len(maobv_list), len(data.Codes)):
                MAOBV[code].append(maobv_list[b])
            a += 1
        return MAOBV

    @classmethod
    def index_mapsy(cls, codes, N):
        """
        PSY心理指标
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:PSY心理指标指标字典 ，key:股票代码，value：指标数值
        """
        MAPSY = {}
        mapsy_list = list()
        data = None
        for n in range(0, N):
            data = c.css(codes, "PSY", "TradeDate={},N1=6,N2=12,Psy=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            mapsy_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            MAPSY[code] = list()
            for b in range(a, len(mapsy_list), len(data.Codes)):
                MAPSY[code].append(mapsy_list[b])
            a += 1
            MAPSY[code].reverse()
        return MAPSY

    @classmethod
    def index_maroc(cls, codes, N):
        """
        ROC变动速率,适用于股票价格变动速率的衡量
        ROC指标在正值以下范围内波动为强势区域，可持股观望；
        ROC值在负值以下范围内波动为弱势区域，可持股观望
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:ROC变动速率指标字典 ,ROC：N日ROC值, ROCMA：N日ROC移动值，key:股票代码，value：指标数值
        """
        ROC = {}
        roc_list = list()
        data = None
        for n in range(0, N):

            data = c.css(codes, "ROC",
                         "TradeDate={},N1=12,N2=6,Roc=1,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            roc_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            ROC[code] = list()
            for b in range(a, len(roc_list), len(data.Codes)):
                ROC[code].append(roc_list[b])
            ROC[code].reverse()
            a += 1
        ROCMA = {}
        rocma_list = list()
        for n in range(0, N):
            data = c.css(codes, "ROC",
                         "TradeDate={},N1=12,N2=6,Roc=2,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            rocma_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            ROCMA[code] = list()
            for b in range(a, len(rocma_list), len(data.Codes)):
                ROCMA[code].append(rocma_list[b])
            ROCMA[code].reverse()
            a += 1
        return ROC, ROCMA

    @classmethod
    def index_marsi(cls, codes, N):
        """
        RSI相对强弱指标,强弱指标的值均在0与100之间,
        强弱指标保持高于50表示为强势市场，反之低于50表示为弱势市场
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:RSI相对强弱指标字典 ，key:股票代码，value：指标数值
        """
        MARSI = {}
        marsi_list = list()
        data = None
        for n in range(0, N):

            data = c.css(codes, "RSI", "TradeDate={},N=6,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            marsi_list.append(data.Data[code][i])

        a = 0
        for code in data.Codes:
            MARSI[code] = list()
            for b in range(a, len(marsi_list), len(data.Codes)):
                MARSI[code].append(marsi_list[b])
            a += 1
            MARSI[code].reverse()

        return MARSI

    @classmethod
    def index_trix(cls, codes, N):
        """
        TRIX三重指数平滑平均
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:TRIX三重指数平滑平均指标字典 ，TRIX:上线, TRMA：下线,key:股票代码，value：指标数值
        """
        TRIX = {}
        trix_list = list()
        data = None
        for n in range(0, N):
            data = c.css(codes, "TRIX",
                         "TradeDate={},N1=12,N2=20,Trix=1,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            trix_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            TRIX[code] = list()
            for b in range(a, len(trix_list), len(data.Codes)):
                TRIX[code].append(trix_list[b])
            TRIX[code].reverse()
            a += 1

        TRMA = {}
        trma_list = list()
        for n in range(0, N):
            data = c.css(codes, "TRIX",
                         "TradeDate={},N1=12,N2=20,Trix=2,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            trma_list.append(data.Data[code][i])

        a = 0
        for code in data.Codes:
            TRMA[code] = list()
            for b in range(a, len(trma_list), len(data.Codes)):
                TRMA[code].append(trma_list[b])
            TRMA[code].reverse()
            a += 1

        return TRIX, TRMA

    @classmethod
    def index_mavol(cls, codes, N):
        """
        成交量指标
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:MAVOL_60MA, MAVOL_20MA, MAVOL_10MA分别为60日，20日和10日移动成交量指标字典 ，key:股票代码，value：指标数值
        """
        data = c.csd(codes, "VOLUME", getdateformtoday(-N - 59), getdateformtoday(0),
                     "period=1,adjustflag=1,curtype=1,order=1,market=CNSESH")
        MAVOL_60MA = {}
        MAVOL_20MA = {}
        MAVOL_10MA = {}
        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request csd Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    MAVOL = list()
                    Datalist = list()
                    for i in range(0, len(data.Indicators)):
                        for j in range(0, len(data.Dates)):  # 保存60+N个数据
                            data.Data[code][i][j] = 0 if data.Data[code][i][j] is None else data.Data[code][i][j]
                            Datalist.append(data.Data[code][i][j])
                    for i in range(0, N):
                        MAVOL.append(round(sum(Datalist[i:i + 59]) / 60, 2))
                        MAVOL.append(round(sum(Datalist[i:i + 19]) / 20, 2))
                        MAVOL.append(round(sum(Datalist[i:i + 9]) / 10, 2))
                    MAVOL_60MA[code] = MAVOL[:N]
                    MAVOL_20MA[code] = MAVOL[N:2 * N]
                    MAVOL_10MA[code] = MAVOL[2 * N:3 * N]
                return MAVOL_60MA, MAVOL_20MA, MAVOL_10MA

    @classmethod
    def index_mawr(cls, codes, N):
        """
        W&R威廉指标
        当威廉指数的值越小，市场越处买方主导，相反越接近零，市场由卖方主导，
        一般来说超过-20%的水平会视为超买（Overbought）的讯号，
        而-80%以下则被视为超卖（Oversold）讯号
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:W&R威廉指标指标字典 ，key:股票代码，value：指标数值
        """
        MAWR = {}
        mawr_list = list()
        data = None
        for n in range(0, N):

            data = c.css(codes, "RSI", "TradeDate={},N={},AdjustFlag=1,Period=1".format(getdateformtoday(-n), N))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                            mawr_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            MAWR[code] = list()
            for b in range(a, len(mawr_list), len(data.Codes)):
                MAWR[code].append(mawr_list[b])
            a += 1
            MAWR[code].reverse()
        return MAWR

    @classmethod
    def index_close(cls, codes, N):
        """
        收盘价移动函数
        :param codes:东财代码
        :param N:移动周期，N为追溯到N天前到现在
        :return:收盘价字典 ，key:股票代码，value：平均收益数值
        """
        CLOSE = {}
        close_list = list()
        data = c.css(codes, "CLOSE", "TradeDate={},AdjustFlag=1".format(getdateformtoday(-N)))
        if not isinstance(data, c.EmQuantData):
            print(data)
        else:
            if data.ErrorCode != 0:
                print("request css Error, ", data.ErrorMsg)
            else:
                for code in data.Codes:
                    for i in range(0, len(data.Indicators)):
                        data.Data[code][i] = 0 if data.Data[code][i] is None else data.Data[code][i]
                        close_list.append(data.Data[code][i])
        a = 0
        for code in data.Codes:
            CLOSE[code] = list()
            for b in range(a, len(close_list), len(data.Codes)):
                CLOSE[code].append(close_list[b])
            a += 1
        return CLOSE

    @staticmethod
    def stoplossparabola(codes, N):
        """

        :param codes:
        :param N:
        :return:
        """

        data = None
        MASAR = {}
        masar_list = list()
        for n in range(0, N):
            data = c.css(codes, "SAR", "TradeDate={},N=4,AdjustFlag=1,Period=1".format(getdateformtoday(-n)))
            if not isinstance(data, c.EmQuantData):
                print(data)
            else:
                if data.ErrorCode != 0:
                    print("request css Error, ", data.ErrorMsg)
                else:
                    for code in data.Codes:
                        for i in range(0, len(data.Indicators)):
                            masar_list.append(data.Data[code][i])

        a = 0
        for code in data.Codes:

            MASAR[code] = list()
            for b in range(a, len(masar_list), len(data.Codes)):
                MASAR[code].append(masar_list[b])
            MASAR[code].reverse()
            a += 1

        return MASAR
