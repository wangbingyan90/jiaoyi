import sys, time
sys.path.append(".")
from strate.config import config
from easytrader import api,exceptions
user = api.use('htzq_client')
user.prepare(config_path=config.homePath+'password.txt')

# for i in range(9):
#     time.sleep(5)
#     print(user.getEntrust()['证券代码'])

# print(user.aout_buy('002127','0.07771','100'))

# 撤单
# user._switch_left_menus(["撤单[F3]"])
# user.have_cancel_entrust(4)