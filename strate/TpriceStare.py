from share import share
from Istrate import Istrate
from config import config

class TpriceStare(Istrate):
    '''
    基本做T
    '''

    def __init__(self,name,step = 0,share = None,price = 0,num = 0,change = 0,have = 0,bug = False):
        super().__init__(name,step,share,price,num,change,have,bug)

    

    def setPrice(self,price):
        if price == 0:
            self.price = self.share.get_now_price()
        else:
            self.price = price
        self.buyPrice = round(self.price - self.change,self.share.decimal)
        self.sellPrice = round(self.price + self.change,self.share.decimal)

    
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
                self.setPrice(self.price)
                self.buy_sell()
                self.step = 15
                self.logger.info(self.state + '调')
        elif self.step == 10:
            self.setPrice(self.price)
            self.buy_sell()
            self.step = 15
            self.logger.info(self.state + '调')
        elif self.step == 15:
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
        
        return True

            



if __name__ == "__main__":
    
    t = TpriceStare(name = '测试',step = 10,share = share('128010'),price = 118,num = 1,change = 1.0,have=10,bug = False)
    config.strateQueue.put(t) 
    t1 = TpriceStare(name = '测试',step = 10,share = share('113038'),price = 210,num = 1,change = 2.0,have=10,bug = False)
    config.strateQueue.put(t1)
    TpriceStare.work()
