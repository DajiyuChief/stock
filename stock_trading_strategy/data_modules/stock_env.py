import math
import sys
from collections import namedtuple
from operator import attrgetter

from gol import set_value,get_value
import numpy as np
import pandas as pd
import pymysql
import tushare as ts
import talib as ta
import datetime
from datetime import date, datetime, timedelta, time
from chinese_calendar import is_workday, is_holiday
import database_connection
pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')


def set_info(start, end, stock):
    global stock_code
    global global_data
    global transaction_date
    global buy_signal, sell_signal
    stock_code = stock
    global_data = setdata(start, end, stock)
    clear()
    # transaction_date = []
    # buy_signal = []
    # sell_signal = []

    # boll线
    global_data['upper'], global_data['middle'], global_data['lower'] = ta.BBANDS(
        global_data.close.values,
        timeperiod=20,
        nbdevup=2,
        nbdevdn=2,
        matype=0)
    global_data['rsi'] = ta.RSI(global_data.close.values, timeperiod=6)
    # global_data['minus'] = global_data['rsi'].diff()
    global_data['rsi_var'] = global_data['rsi'].diff() / np.roll(global_data['rsi'], shift=1)
    global_data['low-lowboll'] = global_data['low'] - global_data['lower']
    global_data['high-highboll'] = global_data['high'] - global_data['upper']
    global_data['high-mid'] = global_data['high'] - global_data['middle']
    global_data['mid-low'] = global_data['middle'] - global_data['low']
    global_data['close-open'] = global_data['close'] - global_data['open']
    global_data['yes_close-mid'] = global_data['pre_close'] - global_data['middle']
    global_data['mid-close'] = global_data['middle'] - global_data['close']
    for i in range(len(global_data)):
        transaction_date.append(global_data.trade_date[i])
    transaction_date = sorted(transaction_date)
    # global_data.to_csv('res' + stock + '.csv')
    set_value(stock_code+'global_data',global_data)
    set_value(stock_code+'transaction_date',transaction_date)
    return global_data


def clear():
    global transaction_date, buy_signal, sell_signal, transaction_signal, middle_date, middle_buy_list, middle_sell_list, all_middle_buy_list, all_middle_sell_list, not_buy_date, not_sell_date
    buy_signal = []
    sell_signal = []
    transaction_signal = []
    middle_date = []
    # 中线条件的买卖日期
    middle_buy_list = []
    middle_sell_list = []
    # 所有上穿，下穿中线时间
    all_middle_buy_list = []
    all_middle_sell_list = []
    not_buy_date = []
    not_sell_date = []


def setdata(start_day, end_day, stock_code):
    while True:
        try:
            df = pro.daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
            if len(df) == 0:
                df = pro.fund_daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
            break
        except:
            continue
    df = df.sort_values(by='trade_date', ascending=True)
    return df


# 获取基金数据


# 计算两个日期之间的交易日
def workdays(start, end):
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


# 日期前推 后推
def date_calculate(date, days):
    start = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
    day = date
    if days > 0:
        while days > 0:
            start += timedelta(days=1)
            day = start.strftime('%Y%m%d')
            if day in transaction_date:
                days = days - 1
    elif days < 0:
        while days < 0:
            start -= timedelta(days=1)
            day = start.strftime('%Y%m%d')
            if day in transaction_date:
                days = days + 1
    return day


# 返回交易时间列表
def used_date(start, end):
    date1 = global_data.loc[global_data['trade_date'] == start].index[0] + 1
    date2 = global_data.loc[global_data['trade_date'] == end].index[0]
    days = global_data[-date1:-date2]['trade_date']
    return days

