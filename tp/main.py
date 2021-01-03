import sys
sys.path.append(".")
from dataQueue import *
from share import share
from option import TOption
import threading
from concurrent.futures import ThreadPoolExecutor

class Tupo:

    def __init__(self,codes):
        '''
        股票池
        '''
        self.shareList = []
        for code in codes:
            self.shareList.append(
                share(code)
            )
        self.len = len(codes)
        self.codes = codes
        self.yes = [False for _ in range(self.len)] # 突破

    
    def chack(self):
        
        for i in range(self.len):
            if self.yes[i]:
                if self.shareList[i].have>0:
                    pass 

            else:
                if self.shareList[i].yesterdayMax() > self.shareList[i].get_now_price():
                    optionQueue.put(TOption('突破交易','buy',self.shareList[i],0,1))

    def quaActiveT(self):
        for share in self.shareList:
            op = TOption('快速做T','buy_sell',share,0,1,1)
            optionQueue.put(op)

            
    def run(self):
        
        while True:

            data = optionRequesQueue.get()

            if data.name == '突破交易' and data.step == 2:
                data.option = '下落五次均线'
                thread1 = threading.Thread(target=data.share.triger,args=(data))
                thread1.start()

def wxmsg():
        while True:
                print(Messagequeue.get())

if __name__ == "__main__": 
    # main = Tupo(['600121'])
    # pool = ThreadPoolExecutor(5)
    # print('启动操作线程')
    # optionThread = pool.submit(TOption.run)

    op = TOption('快速做T','buy_sell','600396',0,1,1)
    optionQueue.put(op)
    thread1 = threading.Thread(target=wxmsg,args=(""))   
    thread1.start()
    print('启动做T')
    # main.quaActiveT()
    TOption.run()
   

    


