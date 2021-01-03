# -*- coding: utf-8 -*-
import logging
from logging import handlers

logger = logging.getLogger("easytrader")
logger.setLevel(logging.INFO)
logger.propagate = False

fmt = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(filename)s %(lineno)s: %(message)s"
)

ch = logging.StreamHandler()
ch.setFormatter(fmt)


# fh = handlers.TimedRotatingFileHandler(filename='logfile.log', when="D", interval=1, backupCount=7,encoding='utf-8')
# fh.suffix = "%Y-%m-%d_%H-%M.log"
# fh.setFormatter(fmt)
# # fh.setLevel(logging.INFO) 

# logger.handlers.append(fh)
logger.handlers.append(ch)