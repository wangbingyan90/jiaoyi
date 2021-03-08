import sys, time, requests, json
sys.path.append(".")
import tushare as ts
from getshare import getshare
import pandas as pd
class share:


    def __init__(self,code):
        self.code = code
        self.have = 0 # 持仓数量
        self.yesterdayMax = None
        self.oneHand = self.iniOneHand()
        self.decimal = self.iniDecimal()
        self.state = False # 状态 是否金叉



    def iniOneHand(self):
        return 10 if self.code[:2] in ['10', '11', '12'] else 100


    def iniDecimal(self):
        return 3 if self.code[:2] in ['16', '15', '51'] else 2 #etf三位


    def get_now_price(self):
        return float(ts.get_realtime_quotes(
            self.code
        )['price'][0])


    def isMa(self,a,b):
        pass


    def addTime(self,start, long):
        s = (start%100 + long)%60
        m = (start%10000/100 + int((start%100 + long)/60))%60
        h = int(start/10000 + int((start%10000/100 + int((start%100 + long)/60))/60))
        return h*10000 + m*100 + s


    def get_data(self,code = '300033',type = 't', date=None, long = '60',retry_count=3, pause=0.001):
        """
            获取交易数据
        Parameters
        ------
            code: string
                    股票代码 e.g. 600848
            type: string, 默认 t
                    数据单位
                    t   : 每笔交易明细
                    t15 : 每15秒一周期
                    t30 : 每30秒一周期
                    m   : 每一分钟一周期
                    m5  : 每5分钟一周期
                    d   : 每一天一周期
                    d5  : 每五天一周期 
            date: string
                    为空时，为当日数据
                    开始日期 format：YYYY-MM-DD
            long: int, 默认 60
                    数据个数
            retry_count : int, 默认 3
                    如遇网络等问题重复执行的次数
            pause : int, 默认 0
                    重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题
        return
        -------
            DataFrame 股票交易数据(DataFrame)
        """

        for _ in range(retry_count):
            time.sleep(pause)
            try:
                if date is None:
                    url = 'http://push2ex.eastmoney.com/getStockFenShi?pagesize=6644&amp;ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wzfscj&pageindex=0&;id=%s&sort=1&ft=1&code=%s&market=%s&_=%s'
                    maker = 1 if code[:1] in ['5', '6', '9'] or code[:2] in ['11', '13'] else 0
                    re = requests.get(url%(self.code, self.code, maker, int(time.time())))
                    lines = json.loads(re.text)['data']['data']
                    df = pd.DataFrame(lines)
                    df['p'] = df['p'].map(lambda x: x/1000)
                    if type[0] == 't'and len(type) ==1 :  
                        bs_type = {'1':u'买入',
                                    '2': u'卖出',
                                    '4': u'-'}
                        df['bs'] = df['bs'].map(lambda x: bs_type[str(x)])
                        

                    elif type[0] == 't':
                        n = int(type[1:])
                        count = self.addTime(91500,n)
                        liopen = []
                        lilow = []
                        lihigh = []
                        liclose = []
                        litime = []

                        liopen.append(df['p'][0])
                        low = df['p'][0]
                        high = df['p'][0]
                        close = df['p'][0]
                        ntime = df['t'][0]

                        for tup in zip(df['t'], df['p']):

                            if tup[0] <= count:
                                if tup[1] > high:
                                    high = tup[1]
                                elif tup[1] < low:
                                    low = tup[1]
                                close = tup[1]
                                ntime = tup[0]

                            else:
                                lilow.append(low)
                                lihigh.append(high)
                                liclose.append(close)
                                litime.append(ntime)

                                liopen.append(tup[1])
                                low = tup[1]
                                high = tup[1]
                                close = tup[1]
                                ntime = tup[0]
                                count = self.addTime(count,n)

                        lilow.append(low)
                        lihigh.append(high)
                        liclose.append(close)
                        litime.append(ntime)
                        df = pd.DataFrame({'time':litime,'open':liopen,'close': liclose, 'low':lilow,'high':lihigh})

            except Exception as e:
                print(e)
            else:
                return df

        raise IOError('获取失败，请检查网络.')


    def kdj(self,a):
        df = self.get_data("113038",'t60')
        low_list = df['low'].rolling(9, min_periods=9).min()
        low_list.fillna(value=df['low'].expanding().min(), inplace=True)
        high_list = df['high'].rolling(9 , min_periods=9 ).max()
        high_list.fillna(value=df['high'].expanding().max(), inplace=True)
        rsv = (df['close'] - low_list) / (high_list - low_list) * 100
        df['k'] = pd.DataFrame(rsv).ewm(com=2).mean()
        df['d'] = df['k'].ewm(com=2).mean()
        df['j'] = 3 * df['k'] - 2 * df['d']
        df['kdj'] = df['k']>df['d']
        a[2] = df.iloc[-1]['close']
        a[3] = self.state
        self.state = df.iloc[-1]['kdj']
        return self.state






        


if __name__=='__main__':
    # s = share(code='300033')
    # print(s.get_data(type='t60'))
    import matplotlib.pyplot as plt
    plt.close("all")
    import numpy as np
    ts = pd.Series(np.random.randn(1000), index=pd.date_range("1/1/2000", periods=1000))
    ts = ts.cumsum()
    ts.plot()
