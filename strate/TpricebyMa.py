from share import share
from Istrate import Istrate
from config import config

class TpricebyMa(Istrate):
    '''
    以Ma为条件做T
    '''

    def __init__(self,name,step = 0,share = None,price = 0,num = 0,change = 0,have = 0,waittime = 7,bug = False):
        super().__init__(name = name,step = step,share = share,price = price,num = num,change = change,have = have,waittime = waittime,bug = bug)


    def setPrice(self,price):
        if price == 0:
            self.price = self.share.get_now_price()
        else:
            self.price = price
        self.buyPrice = round(self.price - self.change,self.share.decimal)
        self.sellPrice = round(self.price + self.change,self.share.decimal)


    def run15(self,df):
        if len(df.loc[df['合同编号'] == self.sellEntrust]) == 0:
            # 完成卖出 涨
            self.cancel_entrust(df,self.buyEntrust)
            self.setPrice(self.sellPrice)
            self.buy_sell()
            self.logger.info(self.state + '涨')
        elif len(df.loc[df['合同编号'] == self.buyEntrust]) == 0:
            # 完成买入 跌
            self.cancel_entrust(df,self.sellEntrust)
            self.setPrice(self.buyPrice)
            self.buy_sell()
            self.logger.info(self.state + '跌')
    

    def run10(self,df):
        a = [5,10,0,False]
        if self.share.kdj(a): # 金叉
            print('交易金叉')
            self.waittime = 3

            if a[3]: # 之前也是金叉
                self.run15(df)
            else: # 死转金
                n = (self.price - a[2])/self.change
                if n < -1.5:
                    self.price = self.price + self.change * (int(-n)+1)
                    self.entrusts = self.sells(self.price,self.change,int(-n)+1)

                elif n < 1.5:
                    self.setPrice(self.price)
                    self.buy_sell()
                    self.logger.info(self.state + '开')
                    return
                
                else:
                    self.price = self.price - self.change * (int(-n)+1)
                    self.entrusts = self.buys(self.price,self.change,int(n)+1)

                self.step = 20

        else: # 死叉
            print('交易死叉')
            self.waittime = 20
            if a[3]: # 之前是金叉
                if len(df.loc[df['合同编号'] == self.sellEntrust]) == 0:
                    self.cancel_entrust(df,self.buyEntrust)
                    self.setPrice(self.sellPrice)
                    self.logger.info(self.state + '死')
                elif len(df.loc[df['合同编号'] == self.buyEntrust]) == 0:
                    self.cancel_entrust(df,self.sellEntrust)
                    self.setPrice(self.buyPrice)
                    self.logger.info(self.state + '死')
                else:
                    self.cancel_entrusts(df,[self.buyEntrust,self.sellEntrust])


    
    def run(self,df = None):

        if self.step == 0 and self.start():#判断开仓操作是否完成
            if self.buy():
                self.step = 5
                self.logger.info(self.state + '买')
            else:
                return False
        elif self.step == 5:
            if len(df.loc[df['合同编号'] == self.buyEntrust]) == 0:
                self.have = self.oneHand
                self.step = 10
                self.logger.info(self.state + '建')
                self.run10(df=df)

        elif self.step == 10:
            self.run10(df=df)

        elif self.step == 20:
            for entrust in self.entrusts:
                if len(df.loc[df['合同编号'] == entrust.entrustcode]) == 0:
                    self.price = entrust.price
                    self.setPrice(price=self.price)
                    self.buy_sell()
                    self.logger.info(self.state + '调整')
                    return
                else:
                    self.cancel_entrust(df=df,entrust=entrust.entrustcode)


            



if __name__ == "__main__":
    
    t1 = TpricebyMa(name = '测试',step = 10,share = share('113038'),price = 176,num = 1,change = 2.0,have=10,waittime = 20,bug = True)
    config.strateQueue.put(t1)
    TpricebyMa.work()
