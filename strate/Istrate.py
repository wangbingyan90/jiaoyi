import abc,os,threading,time,sys

from config import stratelog,config
sys.path.append(".")
from easytrader import api


class Istrate(abc.ABC):

    rerunList = list() # 策略序列

    client = api.use('htzq_client') # 客户端对象

    
    def __init__(self,name,step = 0,share = None, price = 0, num = 0, change = 0, have = 0, bug = False):

        self.step = step # 0为开仓状态，5为进行开仓，10开仓完毕，15进行调仓状态，20为清仓状态
        self.have = have
        self.state = '常'
        self.price = price
        day = time.strftime("%Y-%m-%d", time.localtime())
        filename = config.homePath + day +name +'['+share.code+']'+'.log'
        name = name+'['+share.code+']'
        self.sellEntrust = 'null'
        self.buyEntrust = 'null'
        
        if not bug:
            self.readConfig(filename)

        self.logger = stratelog.stratelog(name,filename,self)
        
        self.name = name
        self.share = share
        self.num = num
        self.oneHand = num * share.oneHand
        self.change = change

    # 读取配置价格
    def readConfig(self,filename):
        # 日志模式 未实现
        if os.path.exists(filename):
            f = open(filename,encoding = 'utf8')
            line = f.readlines()
            try:
                last_line = (line[-1])[:-1].split(',')
                self.step = int(last_line[1])
                state = last_line[3]
                self.price = float(last_line[5])
                self.have = int(last_line[7])
                self.buyEntrust = last_line[9]
                self.sellEntrust = last_line[11]
            except BaseException:
                print('日志读取失败')

    
    def buy(self):
        resoult = Istrate.client.aout_buy(self.share.code
                                            ,self.price
                                            ,self.oneHand)
        if resoult['state'] == 'success':
            self.buyEntrust = resoult['成交合同']
            self.step = 5
            return True
        else:
            print('交易失败')
            print(resoult['content'])
            return False


    def buy_sell(self):
        resoult = Istrate.client.aout_buy_sell(self.share.code
                                            ,self.buyPrice
                                            ,self.sellPrice
                                            ,self.oneHand)
        if resoult['state'] == 'success':
            self.sellEntrust = resoult['卖出合同']
            self.buyEntrust = resoult['买入合同']
            return True
        else:
            if '错误合同' in resoult: 
                if '资金不足' in resoult['content']:
                    self.sellEntrust = resoult['错误合同']
                    self.buyEntrust = resoult['错误合同']                      
                    return True
            else:
                self.logger.info(resoult['content'])
                return False


    # 开仓条件
    def start(self):
        return True


    # 调仓条件
    def adjust(self):
        return True


    # 清除条件及操作
    def end(self):
        return True

    # 取消多个合同
    def cancel_entrusts(self,df,entrusts):
        entrustIndex = []
        for entrust in entrusts:
            if len(df.loc[df['合同编号'] == entrust]) == 0:
                pass
            else:
                entrustIndex.append(int(df.loc[df['合同编号'] == entrust].index[0]) + 1)
        entrustIndex.sort(reverse=True)
        for index in entrustIndex:
            self.client.have_cancel_entrust(index)

    # 取消单个合同
    def cancel_entrust(self,df,entrust):
        # 不存在
        if len(df.loc[df['合同编号'] == entrust]) == 0:
            print('合同消失')
            return False
        else:
            print(int(df.loc[df['合同编号'] == entrust].index[0]))
            self.client.have_cancel_entrust(int(df.loc[df['合同编号'] == entrust].index[0]) + 1)
            return True
    

    @abc.abstractmethod
    def setPrice(self,price):
        pass



    @classmethod
    def initClient(cls):
        cls.client.prepare(config_path = config.homePath + 'password.txt')


    
    @classmethod
    def timeSlot(cls):

        while True:

            s = 20
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
                # print(df)
                for strate in data:
                    strate.run(df)

            else:
                if data.step == 0 or data.step == 10:
                    if data.run():
                        cls.rerunList.append(data)
                    else:
                        pass #操作失败
                else:
                    cls.rerunList.append(data)