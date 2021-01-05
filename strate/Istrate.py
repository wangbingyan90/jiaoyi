import abc,os,threading,time

from easytrader import api
from config import stratelog,config

class Istrate(abc.ABC):

    rerunList = list() # 策略序列

    client = api.use('htzq_client') # 客户端对象

    
    def __init__(self,name,share = None, price = 0, num = 0, change = 0):

        self.step = 0 # 0为开仓状态，1为调仓状态，2，清除状态

        self.logger = stratelog.stratelog(name+'['+share.code+']')
        self.readConfig()

        self.name = name
        self.share = share
        self.num = num
        self.oneHand = num * share.oneHand
        self.change = change


    def readConfig(self, price):
        filename = config.homePath + name+'['+share.code+']'+'.log'
        if os.path.exists(filename):
            f = open(filename,encoding = 'utf8')
            line = f.readlines()
            if len(line) == 0:
                self.price = price # 交易价格
            else:
                last_line = line[-1]
                self.price = float(last_line.split(',')[-1])


    # 开仓条件及操作
    def start(self):
        return True


    # 调仓条件及操作
    def adjust(self):
        return True


    # 清除条件及操作
    def end(self):
        return False

    
    def run(self):

        if self.step == 0:
            self.start()

        elif self.step == 1:
            self.adjust()

        elif self.step == 2:
            self.isFinish()


    
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
                
                for strate in data:
                    strate.run()

            else:
                data.start()
                cls.rerunList.append(data)


