# -*- coding: utf-8 -*-
import logging
from logging import handlers
from dataQueue import *

class oplog():

    
    def __init__(self,name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        fmt = logging.Formatter(
            "[%(asctime)s] %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S %p'
        )

        # ch = logging.StreamHandler()
        # ch.setFormatter(fmt)


        # fh = logging.FileHandler(filename='C:/Users/wby/Desktop/'+name+'.log',encoding='utf-8')
        # fh.setFormatter(fmt)
        # fh.setLevel(logging.INFO) 


        handler = logging.handlers.RotatingFileHandler(filename= cofpath + name+'.log', maxBytes=10000, backupCount=2,encoding='utf-8')
        handler.setFormatter(fmt)

        # logger.handlers.append(fh)
        logger.handlers.append(handler)
        # logger.handlers.append(ch)
        self.logger = logger

    
    def info(self,message):
        return self.logger.info(message)


if __name__ == "__main__":
    op2 = oplog('qqqq')
    for i in range(100):
        op2.info(i)