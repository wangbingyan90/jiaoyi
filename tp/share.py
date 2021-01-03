import sys, time
sys.path.append(".")
import tushare as ts
from getshare import getshare
from dataQueue import *
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


    def getYesterday(self):
        if self.yesterdayMax:
            return self.yesterdayMax

        self.yesterdayMax = ts.get_hist_data(
            self.code,
            start = getshare.getYesterday(),
            end= getshare.getYesterday()
            )['high'][0]
        return self.yesterdayMax


    def sell(self, num, price = 0):
        optionQueue.put(['sell',self,self.oneHand*num,price])
        self.sellHave = num

    
    def finishBuyEntrust(self,option):
        self.have = self.have + option.num


    def finishSellEntrust(self,option):
        self.have = self.have - option.num


    # 在均线上方
    def getTrickMA(self,n):
        sum = 0
        data = getshare.get_today_ticks(self.code).to_dict('list')['price'][0-n]
        for i in data:
            sum = i+ sum

        if i < sum/n:
            return False
        return True

    
    def triger(self,option):

        if option.option == '下落五次均线' and option.step == 2:
            while True:
                if not self.getTrickMA(5):
                    option.option='sell'
                    option.price = 0
                    optionQueue.put(option)
                    break
                time.sleep(2.7)


        


if __name__=='__main__':
    pass