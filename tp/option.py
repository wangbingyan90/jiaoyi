import sys, time,datetime,os, threading
sys.path.append(".")
from easytrader import api,exceptions
from dataQueue import *
from share import share
from oplog import oplog
from easytrader.log import logger
class TOption:

    optionList = list() # 操作序列
    optionER = list() # 后续操作
    client = api.use('htzq_client')

    def __init__(self,name,option,share = None,price = 0,num = 0,ratio = 0):
        '''
        name
        share
        price：价格
        num：
        ratio:
        '''
        self.logger = oplog(name+'['+share.code+']')

        if os.path.exists(cofpath + name+'['+share.code+']'+'.log'):
            f = open( cofpath +name+'['+share.code+']'+'.log',encoding = 'utf8')
            last_line = f.readlines()
            if len(last_line) == 0:
                self.price = price # 交易价格
            else:
                last_line = last_line[-1]
                self.price = float(last_line.split(',')[-1])

        self.name = name
        self.option = option
        self.share = share
        self.num = num * share.oneHand
        self.setp = 1
        self.entrust = None
        self.buyEntrust = None
        self.sellEntrust = None
        self.buyPrice = None
        self.sellPrice = None
        self.rbuyPrice = 1
        self.rsellPrice = 1
        self.ratio = ratio/100
        self.costs = []        
        TOption.optionList.append(self)
        self.chile = None
        self.father = None
        self.circle = 0
        self.initPrice = price


    def getChile(self):
        if self.chile:
            self.chile.initPrice = self.price
            self.chile.price = self.price
            return self.chile
        self.chile = TOption(self.name,self.option,self.share,self.price,self.num/self.share.oneHand,self.ratio*100/2)
        self.chile.father = self
        return self.chile
        


    def addCosts(self,state,price):
        self.price = price
        self.circle = 0
        if price == 0:
            price = self.share.get_now_price()
        if self.name == '快速做T2':
            if self.father:
                state = state + '缩'
                if price == self.initPrice:
                    self.buyPrice = round(price - self.ratio*100,self.share.decimal)
                    self.sellPrice = round(price + self.ratio*100,self.share.decimal)
                elif price ==  round(self.initPrice - self.ratio*100,self.share.decimal):
                    self.buyPrice = round(price - self.ratio*100*3,self.share.decimal)
                    self.sellPrice = round(price + self.ratio*100,self.share.decimal) 
                elif price ==  round(self.initPrice + self.ratio*100,self.share.decimal):
                    self.buyPrice = round(price - self.ratio*100,self.share.decimal)
                    self.sellPrice = round(price + self.ratio*100*3,self.share.decimal)
                elif price ==  round(self.initPrice + self.ratio*100*4,self.share.decimal):
                    self.father.addCosts(state,price) 
                    return True    
                elif price ==  round(self.initPrice - self.ratio*100*4,self.share.decimal):
                    self.father.addCosts(state,price)
                    return True  
            else:
                self.buyPrice = round(price - self.ratio*100,self.share.decimal)
                self.sellPrice = round(price + self.ratio*100,self.share.decimal)
        else:
            self.buyPrice = round(price*(1-self.ratio),self.share.decimal)
            self.sellPrice = round(price*(1+self.ratio),self.share.decimal)
        str1 = state + ','+ str(price)
        print(str1)
        self.logger.info(str1)
        return False


    
    def toChile(self):
        if self.father:
            return False
        else:
            self.circle = self.circle + 1
            if self.circle > 30000:
                return True
            else:
                return False


    
    def optionRun(self):
        if self.option == 'buy_sell':
            resoult = TOption.client.aout_buy_sell(self.share.code
                                            ,self.buyPrice
                                            ,self.sellPrice
                                            ,self.num)
            if resoult['state'] == 'success':
                self.sellEntrust = resoult['卖出合同']
                self.buyEntrust = resoult['买入合同']
                self.rbuyPrice = resoult['buyprice']
                self.rsellPrice = resoult['sellprice']
                return True
            else:
                if '错误合同' in resoult: 
                    if '资金不足' in resoult['content']:
                        # self.logger.info('资金不足,仅完成单边交易')
                        self.sellEntrust = resoult['错误合同']
                        self.buyEntrust = resoult['错误合同']
                        self.rbuyPrice = resoult['buyprice']
                        self.rsellPrice = resoult['sellprice']                        
                        return True
                    # elif  '股票不足' in resoult['content']:
                    #     self.sellEntrust = resoult['错误合同']
                    #     self.buyEntrust = resoult['错误合同']
                    #     self.rbuyPrice = 0
                    #     self.rsellPrice = resoult['sellprice']      
                    #     return True
                    TOption.client.cancel_entrust(resoult['错误合同'])
                return False
                # self.buyEntrust = 1
                # self.sellEntrust = 2
                # return True

        
    

    @classmethod
    def initClient(cls):
        cls.client.prepare(config_path=cofpath+'password.txt')


    @classmethod
    def reUser(cls):
        cls.client.closew()   
        time.sleep(3)  
        cls.initClient()


    @classmethod
    def op_cancel_entrust(cls,entrustList,entrust):
        i = 1
        for e in entrustList:
            if e == entrust:
                cls.client.have_cancel_entrust(i)
                return
            i = i + 1

    @classmethod
    def op_cancel_entrusts(cls,entrustList,entrusts):
        
        ee=[]
        for me in entrusts:
            i = 1
            for e in entrustList:
                if e == me:
                    ee.append(i)
                i = i + 1
        ee.sort(reverse=True)
        for me1 in ee:
            cls.client.have_cancel_entrust(me1)
    

    @classmethod
    def run(cls):

        cls.initClient()
        while True:

            data = optionQueue.get()          
            
            if data == 're':
                entrustList = cls.client.getEntrust().to_dict('list')['合同编号']
                # entrustList = [1,2]
                entrustSet = set(entrustList)
                i=-1
                for option in cls.optionER:
                    i = i + 1
                    if option.option =='buy' and not option.entrust in entrustSet:
                        option.share.finishBuyEntrust(option)
                    elif option.option == 'sell' and not option.entrust in entrustSet:
                        option.share.finishSellEntrust(option)
                    elif option.option == 'buy_sell':

                        if not option.sellEntrust in entrustSet:
                            # 完成卖出 涨
                            cls.op_cancel_entrust(entrustList,option.buyEntrust)
                            if option.addCosts('涨',option.sellPrice):
                                cls.optionER[i] = option.father
                                option = option.father
                            if not option.optionRun():
                                cls.optionER.remove(option)


                        elif not option.buyEntrust in entrustSet:
                            # 完成买入 跌
                            cls.op_cancel_entrust(entrustList,option.sellEntrust)
                            if option.addCosts('跌',option.buyPrice):
                                cls.optionER[i] = option.father
                                option = option.father
                            option.optionRun()


                        else:
                            if option.toChile():
                                cls.op_cancel_entrusts(entrustList,[option.buyEntrust,option.sellEntrust])
                                cls.optionER[i] = option.getChile()
                                option = option.getChile()
                                option.addCosts('缩',option.price)
                                option.optionRun()
             
            else:

                if data.option == 'buy':
                    resoult = cls.client.buy(data.share.code,data.price,data.num)
                    if resoult['state'] == 'success':
                        data.entrust = resoult['成交合同']
                        data.price = resoult['price']
                    else:
                        print('失败')
                        print(resoult)

                if data.option == 'sell':
                    resoult = cls.client.sell(data.share.code,data.price,data.num)
                    if resoult['state'] == 'success':
                        data.entrust = resoult['成交合同']
                        data.price = resoult['price']
                    else:
                        print('失败')
                        print(resoult)
                    
                if data.option == 'buy_sell':
                    data.addCosts('开',data.price)
                    if data.optionRun():
                        cls.optionER.append(data)

def mining():
        now_time = datetime.datetime.now()
        # 获取明天时间
        next_time = now_time
        next_year = next_time.date().year
        next_month = next_time.date().month
        next_day = next_time.date().day
        next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 9:15:00", "%Y-%m-%d %H:%M:%S")
        timer_start_time = (next_time - now_time).total_seconds()
        if timer_start_time > 0:
            time.sleep(timer_start_time)
        else:
            # next_time = now_time + datetime.timedelta(days=+1)
            next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 15:01:00", "%Y-%m-%d %H:%M:%S")
            timer_start_time = (next_time - now_time).total_seconds()
            if timer_start_time < 0:
                next_time = now_time + datetime.timedelta(days=+1)
                next_day = next_time.date().day
                next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 9:15:00", "%Y-%m-%d %H:%M:%S")
                timer_start_time = (next_time - now_time).total_seconds()
                time.sleep(timer_start_time)


c = 0
def dsss():
        global c
        if c > 0:
            c = c - 1
            return 3
        now_time = datetime.datetime.now()
        # 获取明天时间
        # next_time = now_time + datetime.timedelta(days=+1)
        next_time = now_time
        next_year = next_time.date().year
        next_month = next_time.date().month
        next_day = next_time.date().day

        next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 9:16:00", "%Y-%m-%d %H:%M:%S")
        timer_start_time = (next_time - now_time).total_seconds()
        if timer_start_time > 0:
            return timer_start_time
        next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 9:21:00", "%Y-%m-%d %H:%M:%S")
        timer_start_time = (next_time - now_time).total_seconds()                
        if timer_start_time > 0:
            c = timer_start_time/3
            return 3
        next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 9:29:00", "%Y-%m-%d %H:%M:%S")
        timer_start_time = (next_time - now_time).total_seconds()
        #定时器,参数为(多少时间后执行，单位为秒，执行的方法)
        if timer_start_time > 0:
            return timer_start_time
        next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 11:31:00", "%Y-%m-%d %H:%M:%S")
        timer_start_time = (next_time - now_time).total_seconds()
        #定时器,参数为(多少时间后执行，单位为秒，执行的方法)
        if timer_start_time > 0:
            c = timer_start_time/3
            return 3
        next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 12:58:00", "%Y-%m-%d %H:%M:%S")
        timer_start_time = (next_time - now_time).total_seconds()
        if timer_start_time > 0:
            return timer_start_time
        next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 15:00:00", "%Y-%m-%d %H:%M:%S")
        timer_start_time = (next_time - now_time).total_seconds()    
        if timer_start_time > 0:
            c = timer_start_time/3
            return 3
        return 50000



def ree():
    while True:
        s = dsss()

        time.sleep(s)
        if len(TOption.optionER) > 0 and optionQueue.qsize() == 0: # 待改进
            optionQueue.put('re')
            



if __name__ == "__main__":
    # mining()
    op2 = TOption('快速做T2','buy_sell',share('128010'),139.6,2,0.6)
    # op2 = TOption('快速做T1','buy_sell',share('1230611'),132,1,1)

    optionQueue.put(op2)    

    thread2 = threading.Thread(target=ree,args=(''))   
    thread2.start()
 
    print('启动做T')
    TOption.run()
    # print('启动')

