import sys, time
sys.path.append(".")
import tushare as ts
from getshare import getshare
class share:


    def __init__(self,code):
        self.code = code
        self.have = 0 # 持仓数量
        self.yesterdayMax = None
        self.oneHand = self.iniOneHand()
        self.decimal = self.iniDecimal()



    def iniOneHand(self):
        return 10 if self.code[:2] in ['10', '11', '12'] else 100


    def iniDecimal(self):
        return 3 if self.code[:2] in ['16', '15', '51'] else 2 #etf三位


    def get_now_price(self):
        return float(ts.get_realtime_quotes(
            self.code
        )['price'][0])


        


if __name__=='__main__':
    pass