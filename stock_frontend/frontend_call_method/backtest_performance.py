import csv
from func_timeout import func_set_timeout
import func_timeout
import eventlet
import time
import math
import sys, os
import tushare as ts
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta


o_path = os.getcwd()
sys.path.append(o_path)
sys.path.append("../stock_trading_strategy")

from trading_strategy_1 import backtest

sys.path.append("../../stock_trading_strategy/trading_strategy_2/backtest2.py")
from trading_strategy_2 import backtest2

sys.path.append("../../stock_selecting_strategy/stock_pool_new")

pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# 收益率和年化收益率
# 参数依次为股票代码，回测周期，初始本金，用户指定比率， 强制止损比率，是否计算手续费，策略类型True策略一/False策略二，全仓True/加仓False
def annual_yield_span(stock_code, span, principal, percent, stoploss, isCharge, type, isWhole):
    # 策略初始价值
    begin = principal
    # 策略最终价值
    end = principal
    if type:
        end = backtest.backtest1(span, stock_code, principal, percent, stoploss, isCharge, isWhole)
    else:
        end = backtest2.backtest2(span, stock_code, principal, percent, stoploss, isCharge, isWhole)
    dif = end - begin
    earning_rate = dif / begin
    earning_rate = format(earning_rate, '.2%')
    rate = (end / begin - 1) / span * 240
    turnover_rate = format(rate, '.2%')
    return earning_rate, turnover_rate, dif


def annual_yield_date(stock_code, start_day, end_day, principal, percent, stoploss, isCharge, type, isWhole):
    # 策略初始价值
    begin = principal
    # 策略最终价值
    end = principal
    if type:
        end = backtest.date_backtest1(start_day, end_day, stock_code, principal, percent, stoploss, isCharge, isWhole)
    else:
        end = backtest2.date_backtest2(start_day, end_day, stock_code, principal, percent, stoploss, isCharge, isWhole)
    dif = end - begin
    earning_rate = dif / begin
    earning_rate = format(earning_rate, '.2%')
    startday = datetime(int(start_day[0:4]), int(start_day[4:6]), int(start_day[6:8]))
    endday = datetime(int(end_day[0:4]), int(end_day[4:6]), int(end_day[6:8]))
    span = (endday - startday).days
    rate = (end / begin - 1) / span * 240
    turnover_rate = format(rate, '.2%')
    return earning_rate, turnover_rate, dif


# 夏普比率
def sharpe_ratio(stock_code, start_day, end_day):
    df = []
    while True:
        try:
            df = pro.daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
            break
        except:
            continue

    # 无风险利率取3%
    pct = df['pct_chg'] - 0.03/252
    sharp = (pct.mean() * math.sqrt(252))/pct.std()
    sharp = format(sharp, '.4f')
    return sharp


# 最大回撤
def max_drawdown(stock_code, start_day, end_day):
    df = []
    while True:
        try:
            df = pro.daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
            break
        except:
            continue
    highest_close = df['close'].max()
    df['dropdown'] = (1 - df['close'] / highest_close)
    max_dropdown = df['dropdown'].max()
    max_dropdown = format(max_dropdown, '.4f')
    return max_dropdown


# 股票价格变动
def priceChange(stock_code, start_day, end_day):
    df = []
    while True:
        try:
            df = pro.daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
            break
        except:
            continue
    diff = df.loc[0]['close'] - df.loc[len(df)-1]['close']
    percent = diff / df.loc[len(df)-1]['close']
    turnover_rate = format(percent, '.2%')
    return turnover_rate


def get_stock_list():
    # lst = pd.read_csv('../table_1.csv', encoding='gbk')
    lst = pd.read_csv('../../stock_selecting_strategy/stock_pool_new', encoding='gbk')
    res = []
    for i in lst['stock1']:
        if i:
            res.append(i)
    for i in lst['stock2']:
        if i:
            res.append(i)
    for i in lst['stock3']:
        if i:
            res.append(i)
    for i in lst['stock4']:
        if i:
            res.append(i)
    for i in lst['stock5']:
        if i:
            res.append(i)
    # print(res)
    # lst = list(lst.groupby(['行业']))
    # lst = lst.sort_values(by='总分', ascending=False)[0:500]
    return res


def strategy1_pool():
    pool = []
    dif = []
    # lst = get_stock_list()
    lst = pd.read_csv('./stock.csv', encoding='gbk')

    for i in lst:
        sys.stdout = open(os.devnull, 'w')
        try:
            tmp = float(annual_yield_span(i, 30, 1000000, 0.1, 0.3, False, True, True)[2])
        except:
            continue
        sys.stdout = sys.__stdout__

        if tmp > 0:
            pool.append(i)
            dif.append(tmp)
            print(i)
    Z = zip(dif, pool)
    Z = sorted(Z, reverse=True)
    print(Z)
    dif, pool = zip(*Z)

    return pool


def strategy2_pool():
    pool = []
    dif = []
    # lst = get_stock_list()
    lst = pd.read_csv('./stock.csv', encoding='gbk')
    for i in lst:
        sys.stdout = open(os.devnull, 'w')
        eventlet.monkey_patch()
        # 设置超时时间为10秒
        with eventlet.Timeout(10, False):
            # 此处编写可能超时的语句，超时则会跳出这段语句
            try:
                tmp = float(annual_yield_span(i, 30, 1000000, 0.1, 0.3, False, False, True)[2])
            except:
                continue
        sys.stdout = sys.__stdout__

        if tmp > 0:
            # itm = []
            # itm.append(i)
            # itm.append(tmp)
            pool.append(i)
            dif.append(tmp)
            print(i)
    Z = zip(dif, pool)
    Z = sorted(Z, reverse=True)
    print(Z)
    dif, pool = zip(*Z)
    return pool

# 示例
# priceChange('600795.SH', '20200531', '20210531')
# print(annual_yield('600795.SH', 30, 100000, 0.1, 0.1, False, True, True))
# print(strategy2_pool())
# print(get_stock_list())


# with open('strategy1.csv','w',encoding='utf8',newline='') as f :
#     writer = csv.writer(f)
#     writer.writerow(strategy1_pool())


