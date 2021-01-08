from share import share
from TpriceStare import TpriceStare
from config import config

class TSpriceStare(TpriceStare):
    '''
    两次缩放功能
    多次存储iniPrice数组存储问题，且目前没有必要
    '''

    def __init__(self,name,share = None,price = 0,num = 0,change = 0,bug = False):
        super().__init__(name,share,price,num,change,bug)
        self.reCount = 0 # 循环计数器
        self.DFreduce = 1 # 定义可缩小次数
        self.reduce = 1 # 可缩小次数
        self.initPrice = price

    
    def reduceRun(self):
        """
        缩小相关参数
        """
        self.initPrice = self.price
        self.state = '缩' + str(self.reduce)
        self.oneHand = self.oneHand / 2
        self.change = self.change /2


    def coverRiseReduceRun(self):
        if self.DFreduce == self.reduce:
            pass
        elif self.sellPrice == round(self.initPrice + self.change*2,self.share.decimal):
            self.reduce = self.reduce + 1
            if self.DFreduce == self.reduce:
                self.state = '常'
            else:
                self.state = '缩' + str(self.reduce)
            self.oneHand = self.oneHand * 2
            self.change = self.change * 2


    def coverDeclineReduceRun(self):
        if self.DFreduce == self.reduce:
            pass
        elif self.sellPrice == round(self.initPrice - self.change*2,self.share.decimal):
            self.reduce = self.reduce + 1
            if self.DFreduce == self.reduce:
                self.state = '常'
            else:
                self.state = '缩' + str(self.reduce)
            self.oneHand = self.oneHand * 2
            self.change = self.change * 2

    
    def adjust(self,df):

        self.reCount = self.reCount + 1

        if len(df.loc[df['合同编号'] == self.sellEntrust]) == 0:
            # 完成卖出 涨
            self.coverRiseReduceRun()
            self.cancel_entrust(df,self.buyEntrust)
            self.setPrice('涨',self.sellPrice)
            self.optionRun()
            self.reCount = 0

        elif len(df.loc[df['合同编号'] == self.buyEntrust]) == 0:
            # 完成买入 跌
            self.coverDeclineReduceRun()
            self.cancel_entrust(df,self.buyEntrust)
            self.setPrice('跌',self.buyPrice)
            self.optionRun()
            self.reCount = 0

        elif self.reCount > 5 and self.reduce > 0: #缩放执行
            self.reduce = self.reduce - 1
            self.cancel_entrusts(df,[self.sellEntrust,self.buyEntrust])
            self.reduceRun()
            self.setPrice('缩',self.price)
            self.optionRun()
            self.reCount = 0



            



if __name__ == "__main__":
    t = TSpriceStare('测试',share('123061'),136.5,4,2.0,True)
    config.strateQueue.put(t) 
    TpriceStare.work()

