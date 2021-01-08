from share import share
from Istrate import Istrate
from config import config

class TpriceStare(Istrate):
    '''
    基本做T
    '''

    def __init__(self,name,share = None,price = 0,num = 0,change = 0,bug = False):
        super().__init__(name,share,price,num,change,bug)

    

    def setPrice(self,state,price):
        if price == 0:
            self.price = self.share.get_now_price()
        else:
            self.price = price
        self.buyPrice = round(self.price - self.change,self.share.decimal)
        self.sellPrice = round(self.price + self.change,self.share.decimal)
        self.logger.info(self.state + state + ','+ str(price))



    def start(self):
        if True: # 开仓条件
            return self.optionRun()

    
    def adjust(self,df):

        if len(df.loc[df['合同编号'] == self.sellEntrust]) == 0:
            # 完成卖出 涨
            self.cancel_entrust(df,self.buyEntrust)
            self.setPrice('涨',self.sellPrice)
            self.optionRun()

        elif len(df.loc[df['合同编号'] == self.buyEntrust]) == 0:
            # 完成买入 跌
            self.cancel_entrust(df,self.sellEntrust)
            self.setPrice('跌',self.buyPrice)
            self.optionRun()

            



if __name__ == "__main__":
    t = TpriceStare('测试',share('123061'),137.5,5,0.5,bug = True)
    config.strateQueue.put(t) 
    TpriceStare.work()
