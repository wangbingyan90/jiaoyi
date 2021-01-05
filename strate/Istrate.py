import abc,os,threading,time,sys

from config import stratelog,config
sys.path.append(".")
from easytrader import api


class Istrate(abc.ABC):

    rerunList = list() # 策略序列

    client = api.use('htzq_client') # 客户端对象

    
    def __init__(self,name,share = None, price = 0, num = 0, change = 0):

        self.step = 0 # 0为开仓状态，1为调仓状态，2，清除状态
        filename = config.homePath + name+'['+share.code+']'+'.log'
        name = name+'['+share.code+']'
        self.readConfig(price,filename)
        self.logger = stratelog.stratelog(name,filename)
        

        self.name = name
        self.share = share
        self.num = num
        self.oneHand = num * share.oneHand
        self.change = change
        
        self.setPrice('开', price)


    def readConfig(self, price,filename):
        
        if os.path.exists(filename):
            f = open(filename,encoding = 'utf8')
            line = f.readlines()
            if len(line) == 0:
                self.price = price # 交易价格
            else:
                last_line = line[-1]
                self.price = float(last_line.split(',')[-1])


    def optionRun(self):
        resoult = Istrate.client.aout_buy_sell(self.share.code
                                            ,self.buyPrice
                                            ,self.sellPrice
                                            ,self.oneHand)
        if resoult['state'] == 'success':
            self.sellEntrust = resoult['卖出合同']
            self.buyEntrust = resoult['买入合同']
            self.rbuyPrice = resoult['buyprice']
            self.rsellPrice = resoult['sellprice']
            return True
        else:
            if '错误合同' in resoult: 
                if '资金不足' in resoult['content']:
                    self.sellEntrust = resoult['错误合同']
                    self.buyEntrust = resoult['错误合同']
                    self.rbuyPrice = resoult['buyprice']
                    self.rsellPrice = resoult['sellprice']                        
                    return False
            else:
                self.logger.info(resoult['content'])
                return False

    # 开仓条件及操作
    def start(self):
        return True


    # 调仓条件及操作
    def adjust(self):
        return True


    # 清除条件及操作
    def end(self):
        return True

    
    def run(self,df):

        if self.step == 0:
            self.start()

        elif self.step == 1 and self.end():
            self.adjust(df)


    
    @abc.abstractmethod
    def setPrice(self,state,price):
        pass



    @classmethod
    def initClient(cls):
        cls.client.prepare(config_path = config.homePath + 'password.txt')


    
    @classmethod
    def timeSlot(cls):

        while True:

            s = 3
            time.sleep(s)

            if len(cls.rerunList) > 0 and config.strateQueue.qsize() == 0:
                config.strateQueue.put(cls.rerunList)


    @classmethod
    def work(cls):
        
        cls.initClient()
        thread2 = threading.Thread(target=cls.timeSlot,args=(''))   
        thread2.start()

        while True:

            data = config.strateQueue.get()

            if isinstance(data,list):

                df = cls.client.getEntrust()
                
                for strate in data:
                    strate.run(df)

            else:
                if data.start():
                    data.step = 2
                    cls.rerunList.append(data)


