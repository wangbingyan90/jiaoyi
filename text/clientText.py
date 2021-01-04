import sys
sys.path.append(".")
from tp import dataQueue
from easytrader import api,exceptions
user = api.use('htzq_client')
user.prepare(config_path=dataQueue.cofpath+'password.txt')
print(user.getEntrust()['证券代码'])