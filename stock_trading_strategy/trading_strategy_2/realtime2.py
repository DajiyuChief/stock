import math
import sys
from collections import namedtuple
from operator import attrgetter

from data_modules import gol
import numpy as np
import pandas as pd
import pymysql
import tushare as ts
import talib as ta
import datetime
from datetime import date, datetime, timedelta, time
from chinese_calendar import is_workday, is_holiday
import database_connection
from trading_strategy_2.backtest2 import set_info

pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')

# sys.path.append("../data_modules/database_connection.py")
# 初始话全局变量
gol._init()

# 回测前一交易日数据
yesterday_data = pd.DataFrame
# 回测当前交易数据
now_data = pd.DataFrame
# 第二天数据
second_data = pd.DataFrame
# 第三天数据
third_data = pd.DataFrame
# 当前历史数据
history_data = pd.DataFrame
# 至少240日历史数据
history_240 = pd.DataFrame
# 全局数据
global_data = pd.DataFrame
# 对应买卖条件中第三条变化的RSI
variety_rsi = 0.1
# 记录条件三的日期
history_condition = pd.DataFrame
# 记录条件三检测日期
condition_date = date
# 开始日期
gol_start = ''
# 结束日期
gol_end = ''
# 股票代码
stock_code = ''
# 条件三条件标志
condition_flag = 1
# 记录条件三执行几次
condition_step = 0
# 记录买卖信号
transaction_signal = []
# 仓位，单位是股数
num = 0
# 记录buy sell 中的cost
cost = 0
# 数据库
db = database_connection.MySQLDb()
# 总资产
all = 0
# 资金
principal = 0
# 起始资金数，用于判断是否需要强制止损
begin = 0
# 记录交易开放时间
transaction_date = []
# 记录交易时间表
# 买卖日期
buy_signal = []
sell_signal = []
# 记录中线条件不交易的日期
not_buy_date = []
not_sell_date = []
# 特殊条件变化率
special_buy_rsi = 0.2
special_sell_rsi = 0.1
# 记录中线条件的交易日期
middle_date = []
# 中线条件的买卖日期
middle_buy_list = []
middle_sell_list = []
# 所有上穿，下穿中线时间
all_middle_buy_list = []
all_middle_sell_list = []
# 记录中线条件其实日期
middle_start_date = ''
# 中线是否可执行标志位
can_middle_flag = 1
# 记录当前中线条件的所属日期
middle_time = ''
# 记录上次中线条件下买卖的时间
middle_last_date = ''
# 定义结构体储存数据
# 分别是当前时间，优先级，类型（买卖），所属时间（穿中线用）
MyStruct = namedtuple("MyStruct", "date priority type time")
# 显示所有行
pd.set_option('display.max_rows', 1000)
# 显示所有列
pd.set_option('display.max_columns', 1000)

def new_trans(stock_code, stoploss, isCharge, isWhole):
    global can_middle_flag, condition_step, middle_time
    # 止损日期
    stop_signal = check_stop(stoploss)
    trans = buy_signal + sell_signal + stop_signal
    # shanchu
    trans = list(set(trans))
    trans = sorted(trans, key=attrgetter("date"))
    check_stop(stoploss)
    # print(trans)
    # print('buy', buy_signal)
    # print('sell', sell_signal)
    # 记录是否有中线条件执行
    is_middle_processing = 0
    # 记录当前交易类型
    trans_flag = 'buy'
    # 上一次买日期，判断止损
    last_buy_date = trans[0].date
    # 已经交易过的中线日期
    already_trans_middle_date = []
    while len(trans) != 0:
        item = trans[0]
        if len(trans) > 1 and trans[0].date == trans[1].date:
            if trans[0].type != trans[1].type:
                trans.pop(1)
        # if last_trans_date == trans[0].date:
        #     trans.pop(0)
        if trans_flag == 'buy':
            # for item in trans:
            if 'buy' not in item.type:
                trans.pop(0)
                continue
            if item.priority == 1:
                buy(stock_code, isCharge, item.date, isWhole)
                trans.pop(0)
                trans_flag = 'sell'
                last_buy_date = item.date
                condition_step = 0
            elif item.priority == 2:
                if condition_step == 0:
                    if item.time == item.date:
                        # print(2, item.time, item.date)
                        # print(item)
                        middle_time = item.time
                        buy(stock_code, isCharge, item.date, isWhole)
                        trans.pop(0)
                        trans_flag = 'sell'
                        last_buy_date = item.date
                        condition_step = condition_step + 1
                    # item.time != item.date 情况
                    elif date_calculate(item.time,3) > item.date:
                        # print(2, item.time, item.date)
                        middle_time = item.time
                        buy(stock_code, isCharge, item.date, isWhole)
                        trans.pop(0)
                        trans_flag = 'sell'
                        last_buy_date = item.date
                        condition_step = get_middle_position(item.date, item.time) + 1
                    else:
                        # print(item,1)
                        trans.pop(0)
                        continue
                elif item.type == 'notbuy' and item.time == middle_time:
                    # print(item, 2)
                    trans.pop(0)
                    condition_step = condition_step + 1
                elif condition_step < get_middle_len(middle_time) and item.time == middle_time:
                    # print(item.time, item.date,middle_time)
                    buy(stock_code, isCharge, item.date, isWhole)
                    trans.pop(0)
                    trans_flag = 'sell'
                    last_buy_date = item.date
                    condition_step = condition_step + 1
                else:
                    # print(condition_step,item, get_middle_len(middle_time),middle_time)
                    trans.pop(0)
                if condition_step == get_middle_len(middle_time):
                    condition_step = 0
            elif item.priority == 3:
                buy(stock_code, isCharge, item.date, isWhole)
                trans.pop(0)
                trans_flag = 'sell'
                last_buy_date = item.date
                condition_step = 0
        elif trans_flag == 'sell':
            # for item in trans:
            if 'sell' not in item.type and 'stop' not in item.type:
                trans.pop(0)
                continue
            if item.type == 'stop':
                if item.time == last_buy_date:
                    stop_loss(stock_code, isCharge, item.date)
                    trans.pop(0)
                    trans_flag = 'buy'
                    condition_step = 0
                    continue
            if item.priority == 1:
                # print(1, item.time, item.date)
                sell(stock_code, isCharge, item.date)
                trans.pop(0)
                trans_flag = 'buy'
                condition_step = 0
            elif item.priority == 2:
                if condition_step == 0:
                    if item.time == item.date:
                        # print(2,item.time, item.date)
                        middle_time = item.time
                        sell(stock_code, isCharge, item.date)
                        trans.pop(0)
                        trans_flag = 'buy'
                        condition_step = condition_step + 1
                    elif date_calculate(item.time,3) > item.date:
                        # print(2, item.time, item.date)
                        middle_time = item.time
                        sell(stock_code, isCharge, item.date)
                        trans.pop(0)
                        trans_flag = 'buy'
                        last_buy_date = item.date
                        condition_step = get_middle_position(item.date, item.time) + 1
                    else:
                        trans.pop(0)
                        continue
                elif item.type == 'notsell' and item.time == middle_time:
                    trans.pop(0)
                    condition_step = condition_step + 1
                elif condition_step < get_middle_len(middle_time) and item.time == middle_time:
                    # print(2,item.time, item.date)
                    sell(stock_code, isCharge, item.date)
                    trans.pop(0)
                    trans_flag = 'buy'
                    condition_step = condition_step + 1
                else:
                    trans.pop(0)
                if condition_step == get_middle_len(middle_time):
                    condition_step = 0
            elif item.priority == 3:
                sell(stock_code, isCharge, item.date)
                trans.pop(0)
                trans_flag = 'buy'
                condition_step = 0



def trading_strategy2(principa, stock_code, percent, stoploss, span, isCharge, isWhole, transdate):
    global history_240
    global condition_step
    global num
    global cost
    global all
    global principal
    global begin
    global buy_signal, sell_signal, all_middle_buy_list, all_middle_sell_list
    # 回测日期列表
    day = transdate
    # 仓位，单位是股数
    num = 0
    # 总资产数
    principal = principa
    all = principal
    # 起始资金数，用于判断是否需要强制止损
    begin = principal
    # 用迭代器跳过指定天数
    day_iter = iter(day)
    for d in day_iter:
        yesterday = date_calculate(d, -1)
        price = get_price(d, 'close')
        # 单笔交易至少有100股
        if True:
            buy_check(percent, d)
            if buy_check_touch_low(percent, d)[0]:
                span_days = buy_check_touch_low(percent, d)[1]
                new_day = date_calculate(d, span_days)
                price = get_price(new_day, 'close')
                # print('buy 触低线', new_day)
                if not isWhole:
                    sell_check_condition_three(d)
                    if condition_step == 0:
                        buy_signal.append(MyStruct(new_day, 3, 'buy', new_day))
                else:
                    buy_signal.append(MyStruct(new_day, 3, 'buy', new_day))
        # 确保有可卖出的股数
        if True:
            sell_check(percent, d)
            if sell_check_touch_high(percent, d)[0]:
                span_days = sell_check_touch_high(percent, d)[1]
                new_day = date_calculate(d, span_days)
                price = get_price(new_day, 'close')
                # print('sell 触高线', new_day)
                if not isWhole:
                    buy_check_condition_three(d)
                    if condition_step == 0:
                        sell_signal.append(MyStruct(new_day, 3, 'sell', new_day))
                else:
                    sell_signal.append(MyStruct(new_day, 3, 'sell', new_day))
            check_middle(yesterday, d)
        # 强制止损
        if num != 0 and all < begin and abs(all - principal - begin) >= stoploss * (all - principal):
            stop_loss(stock_code, isCharge, d)
    # transaction(stock_code, stoploss, isCharge, isWhole)
    new_trans(stock_code, stoploss, isCharge, isWhole)

    print("共计： " + str(span) + "个交易日")
    print('---------------------------------------------------------------------------------------------------------')
    print('---------------------------------------------------------------------------------------------------------')
    return all

def realtime(stock_code, principal, percent, stoploss, isCharge, isWhole):
    global gol_end
    end = date.today()
    offset1 = timedelta(days=-(240 * 1.5 + 100))
    offset2 = timedelta(days=-120)
    # 日期格式化
    start = end + offset1
    end_ymd = end.strftime('%Y%m%d')
    gol_end = end_ymd
    start_ymd = (end + offset1).strftime('%Y%m%d')
    start_ymd_real = (end + offset2).strftime('%Y%m%d')
    # 第一次设置用来获取真实交易时间
    set_info(start_ymd_real,end_ymd,stock_code)
    transdate = global_data['trade_date'].values
    # 第二次设置长时间，保证取到所有需要的值
    set_info(start_ymd,end_ymd,stock_code)
    db = database_connection.MySQLDb()
    db.clean_table("TRUNCATE TABLE `actual2`;")
    return trading_strategy2(principal, stock_code, percent, stoploss, 120, isCharge, isWhole, transdate)