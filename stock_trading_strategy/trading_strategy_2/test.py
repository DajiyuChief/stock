from collections import namedtuple
from datetime import datetime

import numpy as np
import pandas as pd

from trading2 import getBoll
import gol
from backtest2 import setdata, date_calculate, set_info,date_backtest2
from backtest2 import getRSI
import talib as ta
import tushare as ts
from backtest2 import workdays
from chinese_calendar import is_workday
from datetime import datetime, timedelta
from chinese_calendar import is_holiday

MyStruct = namedtuple("MyStruct", "date type")

pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')

class DateType:
    def __init__(self, **data):
        self.__dict__.update(data)

def getBoll(df):
    # global history_data
    # if date is None:
    #     df = history_data
    # else:
    #     df = setdata(start_day,date,stock_code)
    high, middle, low = ta.BBANDS(
        df['close'].values,
        timeperiod=20,
        # 与平均值的无偏倚标准差的数量
        nbdevup=2,
        nbdevdn=2,
        # 移动平均线类型：0为简单移动平均线
        matype=0)
    # high: getBoll()[0]
    # print('getBoll')
    return high, middle, low


def newget(data):
    data['upper'], data['middle'], data['lower'] = ta.BBANDS(
        data.close.values,
        timeperiod=20,
        nbdevup=2,
        nbdevdn=2,
        matype=0)


def get_boll(date):
    data = setdata('20220320', '20220615', '600256.SH')
    newget(data)
    high = data.loc[data['trade_date'] == date].upper.values[0]
    middle = data.loc[data['trade_date'] == date].middle.values[0]
    low = data.loc[data['trade_date'] == date].lower.values[0]
    return high, middle, low


def tradedays(start, end):
    # 字符串格式日期的处理
    if type(start) == str:
        start = datetime.strptime(start, '%Y-%m-%d').date()
    if type(end) == str:
        end = datetime.strptime(end, '%Y-%m-%d').date()
    # 开始日期大，颠倒开始日期和结束日期
    if start > end:
        start, end = end, start

    counts = 0
    while True:
        if start > end:
            break
        if is_holiday(start) or start.weekday() == 5 or start.weekday() == 6:
            start += timedelta(days=1)
            continue
        counts += 1
        start += timedelta(days=1)
    return counts


def get_funds_data(code):
    df = pro.fund_daily(**{
        "trade_date": "",
        "start_date": "",
        "end_date": "",
        "ts_code": code,
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "pre_close",
        "open",
        "high",
        "low",
        "close",
        "change",
        "pct_chg",
        "vol",
        "amount"
    ])
    return df


def date_calculate(date, days):
    start = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
    if days >= 0:
        while days > 0:
            if is_holiday(start) or start.weekday() == 5 or start.weekday() == 6:
                start += timedelta(days=1)
                continue
            days -= 1
            start += timedelta(days=1)
    else:
        while days < 0:
            start -= timedelta(days=1)
            if is_holiday(start) or start.weekday() == 5 or start.weekday() == 6:
                start -= timedelta(days=1)
                continue
            days += 1
    day = start.strftime('%Y%m%d')
    return day


def date_calculate2(date, days):
    start = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
    delta = timedelta(days=days)
    n_days_forward = start + delta
    n_days_forward = n_days_forward.strftime('%Y%m%d')
    return n_days_forward


# print(date_calculate2('20220520',2))
# print(date_calculate('20220520',-5))
# print(get_funds_data('516950.SH'))
# data = pd.DataFrame
# data = set_info('20220320', '20220615', '600256.SH')
# data['rsi_var'] = data['rsi'].diff()/np.roll(data['rsi'], shift=1)
# data['low-lowboll'] = data['low'] - data['lower']
# data['high-highboll'] = data['high'] - data['upper']
# data['high-mid'] = data['high'] - data['middle']
# data['mid-low'] = data['middle'] - data['low']
# data['close-open'] = data['close'] - data['open']
# data['yes_close-mid'] = data['pre_close'] - data['middle']
# data['mid-close'] = data['middle'] - data['close']
# data.to_csv('test1.csv')
# print(data)
# print(data.loc[data['trade_date'] == '20220325'])
# print(data2)
# def run():
#     gol.set_value('')
# date_backtest2('20220316', '20220607', '601009.SH', 9999999, 0.1, 0.3, False, True)
date1 = DateType(date = '2022' ,type = '1')
m = MyStruct('20220202','1')
print(m)
print(m.date)
print(m.type)
# print(date1.date)
# print(date1.type)
