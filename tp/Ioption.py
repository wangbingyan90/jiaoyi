import abc,os,dataQueue
from oplog import oplog
from easytrader import api,exceptions

class Ioption(abc.ABC):


    optionList = list() # 操作序列
    optionER = list() # 后续操作
    client = api.use('htzq_client')

    
    def __init__(self,name,share = None,price = 0,num = 0,change = 0):

        self.logger = oplog(name+'['+share.code+']')
        if os.path.exists(dataQueue.cofpath + name+'['+share.code+']'+'.log'):
            f = open(dataQueue.cofpath +name+'['+share.code+']'+'.log',encoding = 'utf8')
            last_line = f.readlines()
            if len(last_line) == 0:
                self.price = price # 交易价格
            else:
                last_line = last_line[-1]
                self.price = float(last_line.split(',')[-1])

        self.name = name
        self.share = share
        self.num = num * share.oneHand

        self.buyEntrust = None
        self.sellEntrust = None

        self.buyPrice = None
        self.sellPrice = None

        self.change = change
        self.costs = []



    @abc.abstractmethod
    def start(self):
        pass



    @abc.abstractmethod
    def reRun(self):
        pass



    @abc.abstractmethod
    def setPrice(self,state,price):
        pass



    @classmethod
    def initClient(cls):
        cls.client.prepare(config_path = dataQueue.cofpath+'password.txt')



    @classmethod
    def run(cls):
        
        cls.initClient()
        while True:

            if data == 're':


            else:

