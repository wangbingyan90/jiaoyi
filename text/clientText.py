import sys
sys.path.append(".")
from strate.config import config
from easytrader import api,exceptions
user = api.use('htzq_client')
user.prepare(config_path=config.homePath+'password.txt')
print(user.getEntrust()['证券代码'])