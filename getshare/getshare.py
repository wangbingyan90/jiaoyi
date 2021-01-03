import json, requests, time, os
import pandas as pd
import tushare as ts
from urllib.request import urlopen, Request
import datetime
import pickle
import akshare as ak

def code_to_symbol(code):
    '''
    生成symbol代码标志
    '''
    return 'sh%s'%code if code[:1] in ['5', '6', '9'] or code[:2] in ['11', '13'] else 'sz%s'%code

bs_type = {'1':u'买入',
           '2': u'卖出',
           '4': u'-'}


# 获取当天的tick
def get_today_ticks(code=None, retry_count=3, pause=0.001):
    url = 'http://push2ex.eastmoney.com/getStockFenShi?pagesize=6644&amp;ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wzfscj&pageindex=0&;id=%s&sort=1&ft=1&code=%s&market=%s&_=%s'
    for _ in range(retry_count):
        time.sleep(pause)
        try:
            maker = 1 if code[:1] in ['5', '6', '9'] or code[:2] in ['11', '13'] else 0

            re = Request(url%(code, code, maker, int(time.time())))
            lines = urlopen(re, timeout=10).read()
            lines = json.loads(lines)
            lines = lines['data']['data']
            df = pd.DataFrame(lines)  
            df = df.rename(columns={'t': 'time', 'p': 'price', 'v': 'vol', 'bs': 'type'})
            df = df[['time', 'price', 'vol', 'type']]
            df['price'] = df['price'].map(lambda x: x/1000)
            df['type'] = df['type'].map(lambda x: bs_type[str(x)])
            df['time'] = df['time'].map(lambda x: str(x).zfill(6))
        except Exception as e:
            print(e)
        else:
            return df[12:]
    raise IOError('网络失败')



# 获取 时间段 数据
def get_min_data(code="113581",len="1",long = '240'):
    '''
    len:数量长度 120 238
    long:时间区间 仅支持 1 5 15 30 60 120 240
    '''
    code = code_to_symbol(code)
    url = "https://quotes.sina.cn/cn/api/jsonp_v2.php/=/CN_MarketDataService.getKLineData"
    params = {
        "symbol": code,
        "scale": long,
        "datalen": len,
    }

    r = requests.get(url, params=params)
    str1 = r.text.split('=(')[1].split(");")[0]
    if str1 == 'null':
        return None
    temp_df = pd.DataFrame(json.loads(str1))


    # for key in ['open','high','low','close','ma_price5','ma_volume5','ma_price10','ma_volume10','ma_price30','ma_volume30']:
    #     temp_df[key] = pd.to_numeric(temp_df[key])
    for key in ['open','high','low','close']:
        temp_df[key] = pd.to_numeric(temp_df[key])
    return temp_df.iloc[:,[0,1,2,3,4]]


def get_min_datas(codes=["113581"],len="21",long = '240'):
    temp_df = None
    for code in codes:
        temp_df1 = get_min_data(code,len,long)
        temp_df = pd.concat([temp_df,temp_df1],ignore_index=True)
    return temp_df

# n天前
def getDay(n): 
    
    if datetime.date.today().weekday() == 0:
        i = -1*n - 1
    elif datetime.date.today().weekday() == 6:
        i = -1*n - 2
    else:
        i = -1*n
    return str(datetime.date.today() + datetime.timedelta(i))


yesterday = None
# 昨天
def getYesterday(): 
    global yesterday
    if yesterday:
        return yesterday
    import datetime
    i = -1
    if datetime.date.today().weekday() == 0:
        i = -3
    yesterday = str(datetime.date.today() + datetime.timedelta(i))
    return yesterday



# 昨天的股票数据
def get_yesterday_datas(codes=["113581"]):
    temp_df = None
    for code in codes:
        temp_df1 = ts.get_hist_data(code,start = getYesterday(),end= getYesterday())
        temp_df = pd.concat([temp_df,temp_df1],ignore_index=True)
    return temp_df.iloc[:,[0,1,2,3,4]]



def shareDay(code,days = 0):
    return ts.get_hist_data(code,start = getDay(0),end= getDay(days))

def select20(row):
    code = row['基金代码']
    df = get_min_data(code,30)
    row['类型'] = df["close"][-10:].mean() < df.iloc[-1]["close"] and df["close"][-30:].mean() < df.iloc[-1]["close"]
    row['单位净值'] = df["close"][-5:].mean() < df.iloc[-1]["close"]
    # print(df)
    # if len(df['close']) == 30:
    #     # print(df.iloc[-1]["close"])
    #     # print(df["close"][-5:].mean())
    #     # print(df["close"][-20:].mean())
    #     # print(df["close"][-30:].mean())
    #     # return df["close"][-5:].mean() < df.iloc[-1]["close"] ,df["close"][-10:].mean() < df.iloc[-1]["close"] ,df["close"][-30:].mean() < df.iloc[-1]["close"]
    #     if df["close"][-10:].mean() < df.iloc[-1]["close"] and df["close"][-30:].mean() < df.iloc[-1]["close"]:
    #         print(code)
    
    # else:
    #     # print(code+'不足20')
    #     pass

def select():
    # c = ak.bond_zh_hs_cov_spot()  # 实时行情数据
    # c = ak.bond_zh_cov()# 可转债数据一览表
    d = ak.bond_cov_comparison() # 可转债比价表
    d = d[d['转股溢价率'] < 20] # 选择
    x = d['最新价'] == '-'
    c = d[x == False]
    x = c['最新价'] < 100
    c = c[x == False]
    # d['转股溢价率'].mean()
    c = c.sort_values(by='转股溢价率').iloc[:,[3,4,9,10,13]]
    return c
    # c = d.sort_values(by='转股溢价率').iloc[:,[0,3,4,9,10,13,18]][0:200]
    # # c = d.sort_values(by='转股溢价率').iloc[:,[0,3,4,13,18]][0:50]
    # x = c['最新价'] == '-'
    # c = c[x == False]
    # x = c['最新价'] < 100
    # c = c[x == False]


# c = select()
# print(len(c))
# i = 0
# for tup in zip(c['正股代码'],c['转债代码'],c['转债名称']):
#     code = tup[0]
#     df = get_min_data(code,30)
#     if df["close"][-10:].mean() < df["close"][-5:].mean():
#         i = i + 1
#         print(tup[1],tup[2])
# print(i)

def getMap():
    path = 'C://Users//wby//Documents//date//level.pkl'
    if os.path.isfile(path):
        f = open(path, 'rb')
        return pickle.load(f)

    pro = ts.pro_api(token='1c8b06446534ae510c8c68e38fc248b99f89ac3814cb55645ae2be72')
    f = open(path, 'wb')

    #获取申万一级行业列表
    code_level = {}
    l1 = pro.index_classify(level='L1', src='SW')
    for i,r in l1.iterrows():
        df = pro.index_member(index_code=r['index_code'])
        for j,rr in df.iterrows():
            if rr['con_code'][:-3] == '300059':
                a = 1
            if not rr['con_code'][:-3] in code_level.keys():
                code_level[rr['con_code'][:-3]] = [[r['index_code'],r['industry_name']],[],[]]
            else:
                code_level[rr['con_code'][:-3]][0].append(r['index_code'])
                code_level[rr['con_code'][:-3]][0].append(r['industry_name'])

    # #获取申万二级行业列表
    l2 = pro.index_classify(level='L2', src='SW')
    for i,r in l2.iterrows():
        df = pro.index_member(index_code=r['index_code'])
        for j,rr in df.iterrows():
            if rr['con_code'][:-3] == '300059':
                a = 1
            code_level[rr['con_code'][:-3]][1].append(r['index_code'])
            code_level[rr['con_code'][:-3]][1].append(r['industry_name'])


    # #获取申万三级级行业列表
    l3 = pro.index_classify(level='L3', src='SW')
    for i,r in l3.iterrows():
        df = pro.index_member(index_code=r['index_code'])
        for j,rr in df.iterrows():
            if rr['con_code'][:-3] == '300059':
                a = 1
            code_level[rr['con_code'][:-3]][2].append(r['index_code'])
            code_level[rr['con_code'][:-3]][2].append(r['industry_name'])

    pickle.dump(code_level, f) #写入文件
    f.close()  #关闭文件
    return code_level

def etf():
    d = ak.fund_em_etf_fund_daily()
    # print(d['市价'])
    x = d['市价'] == '---'
    d = d[x == False]
    d['市价'] = pd.to_numeric(d['市价'])
    d = d[d['市价'] < 5]
    d= d[d['类型'] == 'ETF-场内' ]
    return d.iloc[:,[0,1,2,3]]

# e = etf()
# for index,row in e.iterrows():
#     select20(row)
# from wxpy import * 
# embed()
# e= e[e['类型'] == True ]
# e= e[e['单位净值'] == True ]
# e.to_csv('ko.csv')



def zhuT(a,d = 0.5,ccc = 1):
    sum = 115*21
    csum = 0
    pri = 115
    # print(a.iloc[2]['time'])
    i = 0
    c = 0
    for b in a['price']:
        if b >= (pri+d):
            pri = pri + d
            print('\033[31m'+str(b) + '\t' + str(a.iloc[i]['time']) +'\033[0m')
            c = c - ccc
            csum = csum + pri * ccc
        elif b <= (pri-d):
            pri = pri - d
            print(str(b) + '\t' + str(a.iloc[i]['time']))
            c = c +  ccc
            csum = csum - pri  * ccc
        i = i + 1
    print(str(csum) + '\t' +str( -csum/c)  + '\t' +str( -c))
    print(-csum/c)


def zhuTp(a,d = 0.5,ccc = 1):
    sum = 115*21
    csum = 0
    pri = 148.01
    # print(a.iloc[2]['time'])
    i = 0
    c = 0
    p = 0
    add = 0
    for b in a['price']:
        if b >= (pri+d):
            b = b + 1
            pri = pri + d
            print('\033[31m'+str(b) + '\t' + str(a.iloc[i]['time']) +'\033[0m')
            c = c - ccc
            csum = csum + pri * ccc
            p = 4
        elif b <= (pri-d):
            b = b - 1
            pri = pri - d
            print(str(b) + '\t' + str(a.iloc[i]['time']))
            c = c +  ccc
            csum = csum - pri  * ccc
            p = 4
        # elif p > 0:
        #     p = p - 1
        #     print( '\t' +str(b) + '\t' + str(a.iloc[i]['time']))
        i = i + 1
    print(str(csum) + '\t' +str( -csum/c)  + '\t' +str( -c))
    print(csum)



# a = get_today_ticks('128010')

def Dudal(a,d = 0.25,hand = 1):

    income = 0
    have = 0
    pri = 148
    i = 1
    a['ma'] = a['price'].rolling(window=5).mean() 
    for b in a['price']:
        if b >= (pri+d) and a.iloc[i-1]['ma'] < b:
            income = income - a.iloc[i]['price']
            pri = pri + d
            have = have + 1
            print('买入')
            print(a.iloc[i]['price'])
        elif b <= (pri-d):
            if have > 0:
                income = income + a.iloc[i]['price']*have
                have = 0
                print('卖出')
                print(a.iloc[i]['price'])
                print(income)
            pri = pri- d
            print(pri)
        i = i + 1







# a = get_today_ticks('113038')
# aaa(a,0.25,0.5)
# aaa(a,0.3,0.6)
# aaa(a,1,2)
# aaa(a,1.5,3)
# aaa(a,2,4)
# aaa(a,2.5,5)
# aaa(a,3,6)

# aaap(a,0.5,1)
