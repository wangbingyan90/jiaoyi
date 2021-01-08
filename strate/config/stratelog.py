# -*- coding: utf-8 -*-
import logging
from logging import handlers

from config import config

class stratelog():

    
    def __init__(self,name,filename):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        # 格式
        fmt = logging.Formatter(
            "[%(asctime)s] %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S %p'
        )

        # 屏幕打印
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)

        # 文本打印
        # fh = logging.FileHandler(filename='C:/Users/wby/Desktop/'+name+'.log',encoding='utf-8')
        # fh.setFormatter(fmt)
        # fh.setLevel(logging.INFO) 

        # 自定义打印
        handler = logging.handlers.RotatingFileHandler(filename= filename, maxBytes=10000, backupCount=2,encoding='utf-8')
        handler.setFormatter(fmt)

        # 注册
        # logger.handlers.append(fh)
        logger.handlers.append(ch)
        logger.handlers.append(handler)
        self.logger = logger

    
    def info(self,message):
        return self.logger.info(message)


if __name__ == "__main__":
    op2 = stratelog('qqqq')
    for i in range(100):
        op2.info(i)