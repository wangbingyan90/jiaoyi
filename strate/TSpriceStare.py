from share import share
from TpriceStare import TpriceStare
from config import config

class TSpriceStare(TpriceStare):
    '''
    基本做T
    '''

    def __init__(self,name,share = None,price = 0,num = 0,change = 0):
        super().__init__(name,share,price,num,change)


    def start(self):
        if True: # 开仓条件
            return self.optionRun()

    
    def adjust(self,df):

        if len(df.loc[df['合同编号'] == self.sellEntrust]) == 0:
            # 完成卖出 涨
            self.client.have_cancel_entrust(df.loc[df['合同编号'] == self.buyEntrust].index[0])
            self.setPrice('涨',self.sellPrice)
            self.optionRun()

        elif len(df.loc[df['合同编号'] == self.buyEntrust]) == 0:
            # 完成买入 跌
            self.client.have_cancel_entrust(df.loc[df['合同编号'] == self.sellEntrust].index[0])
            self.setPrice('跌',self.buyPrice)
            self.optionRun()


            



if __name__ == "__main__":
    t = TSpriceStare('测试',share('128010'),139,2,0.8)
    config.strateQueue.put(t) 
    TpriceStare.work()
