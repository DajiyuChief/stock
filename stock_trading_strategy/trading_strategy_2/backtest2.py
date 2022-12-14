import math
import sys
from collections import namedtuple
from operator import attrgetter

import gol
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


# 比较三天之内每前后两天的RSI
def compare_RSI(day1, day2, day3, baseline, flag):
    rsi_day1 = getRSI(day1)
    rsi_day2 = getRSI(day2)
    rsi_day3 = getRSI(day3)
    if flag == 1:
        if rsi_day2 > (1 + baseline) * rsi_day1 or rsi_day3 > (1 + baseline) * rsi_day2:
            return True
        else:
            return False
    elif flag == -1:
        if rsi_day2 > (1 - baseline) * rsi_day1 or rsi_day3 > (1 - baseline) * rsi_day2:
            return True
        else:
            return False


def sell_compare_RSI(day1, day2, day3, baseline):
    rsi_day1 = getRSI(day1)
    rsi_day2 = getRSI(day2)
    rsi_day3 = getRSI(day3)
    if rsi_day2 > (1 + baseline) * rsi_day1 or rsi_day3 > (1 + baseline) * rsi_day2:
        return True
    else:
        return False


def set_cost(date, principal, isWhole):
    price = get_price(date, 'close')
    cost = int(principal / (price * 100))
    if not isWhole:
        # 加仓2p-1
        cost = ((0.7 + winning_percentage()) * 2 - 1) * cost
        # 取满100股
        cost = math.floor(cost / 100) * 100
    return cost


def get_price(date, type):
    if type == 'close':
        return global_data.loc[global_data['trade_date'] == date].close.values[0]
    elif type == 'open':
        return global_data.loc[global_data['trade_date'] == date].open.values[0]
    elif type == 'high':
        return global_data.loc[global_data['trade_date'] == date].high.values[0]
    elif type == 'low':
        return global_data.loc[global_data['trade_date'] == date].low.values[0]


def get_timestamp(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d").timestamp()


# def load_historical_data(stock_code, start_day, end_day):
#     df = pro.daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
#     global yesterday_data
#     yesterday_data = df.loc[1]
#     global now_data
#     now_data = df.loc[0]
#     df = df.sort_values(by='trade_date', ascending=True)
#     global history_data
#     history_data = df
#     return


# 改写getBoll()
def getBoll(date):
    global global_data
    high = global_data.loc[global_data['trade_date'] == date].upper.values[0]
    middle = global_data.loc[global_data['trade_date'] == date].middle.values[0]
    low = global_data.loc[global_data['trade_date'] == date].lower.values[0]
    return high, middle, low


# 改写getRSI()
def getRSI(date):
    global global_data
    # # 6日rsi
    rsi = global_data.loc[global_data['trade_date'] == date].rsi.values[0]
    return rsi


def RSI_vary(date):
    todayRSI = getRSI(date)
    yesRSI = getRSI(date_calculate(date, -1))
    var = (todayRSI - yesRSI) / yesRSI
    return var


# 检测特殊情况中有无触高、低线情况
def check_span_days(start, end, type):
    # 从第二天开始比较
    start = date_calculate(start, 1)
    if type == 'buy':
        while start < end:
            high = get_price(start, 'high')
            highBoll = getBoll(start)[0]
            if high >= highBoll:
                return False
            start = date_calculate(start, 1)
        return True
    if type == 'sell':
        while start < end:
            low = get_price(start, 'high')
            lowBoll = getBoll(start)[2]
            if low <= lowBoll:
                return False
            start = date_calculate(start, 1)
        return True


# 检查中线条件
def check_middle(last_date, date):
    global variety_rsi
    global condition_flag
    global condition_step
    global middle_date, middle_buy_list, middle_sell_list, middle_start_date, middle_last_date
    flag = []
    nextday_index = -1
    day2 = date_calculate(date, 1)
    day3 = date_calculate(day2, 1)
    day4 = date_calculate(day3, 1)
    flag.append(buy_check_middle(last_date, date) or sell_check_middle(last_date, date))
    if flag[0] is True:
        # 第一次不看rsi变化率
        if condition_flag == 1:
            middle_last_date = date
            middle_start_date = date
            if buy_check_middle(last_date, date):
                buy_signal.append(MyStruct(date, 2, 'buy', middle_start_date))
                middle_buy_list.append(MyStruct(date, 2, 'buy', middle_start_date))
            else:
                sell_signal.append(MyStruct(date, 2, 'sell', middle_start_date))
                middle_sell_list.append(MyStruct(date, 2, 'sell', middle_start_date))
            # middle_date.append(MyStruct(date,2))
            condition_flag = condition_flag - 1
        else:
            if abs(RSI_vary(date)) > variety_rsi:
                variety_rsi = variety_rsi * 1.5
                middle_last_date = date
                if buy_check_middle(last_date, date):
                    buy_signal.append(MyStruct(date, 2, 'buy', middle_start_date))
                    middle_buy_list.append(MyStruct(date, 2, 'buy', middle_start_date))
                else:
                    sell_signal.append(MyStruct(date, 2, 'sell', middle_start_date))
                    middle_sell_list.append(MyStruct(date, 2, 'sell', middle_start_date))
            else:
                # 穿中线但rsi变化率不满足时
                middle_last_date = last_date
                if buy_check_middle(last_date, date):
                    buy_signal.append(MyStruct(date, 2, 'notbuy', middle_start_date))
                    middle_buy_list.append(MyStruct(date, 2, 'notbuy', middle_start_date))
                else:
                    sell_signal.append(MyStruct(date, 2, 'notsell', middle_start_date))
                    middle_sell_list.append(MyStruct(date, 2, 'notsell', middle_start_date))
                # variety_rsi = variety_rsi * 1.5
        # 记录与上次中线交易日相比，是否满足穿中线的条件
        for day in [day2, day3, day4]:
            if day2 > date_calculate(middle_last_date, 3):
                flag.append(False)
            elif middle_last_date == last_date:
                flag.append(buy_check_middle(middle_last_date, day) or sell_check_middle(middle_last_date, day))
            else:
                flag.append(buy_check_touch_middle(day) or sell_check_touch_middle(day))
        del (flag[0])
        for i in range(0, 3):
            if flag[i] is True:
                nextday_index = i
                break
        if nextday_index != -1:
            # variety_rsi = variety_rsi * 1.5
            # next_date是除了一次的穿中线的第二天
            next_date = date_calculate(date, nextday_index + 1)
            # print(middle_last_date,next_date,variety_rsi)
            check_middle(middle_last_date, next_date)
        else:
            # print(date)
            # 下穿
            if get_price(date, 'close') < getBoll(date)[1]:
                # 看后三天有没有上穿
                for i in range(1,4):
                    if buy_check_middle(date, date_calculate(date, i)):
                        # fourdays_later四天后，若收盘价高于中线，买入
                        fourdays_later = date_calculate(date, 4)
                        if get_price(fourdays_later, 'close') > getBoll(fourdays_later)[1]:
                            buy_signal.append(MyStruct(fourdays_later, 2, 'buy', middle_start_date))
                            middle_buy_list.append(MyStruct(fourdays_later, 2, 'buy', middle_start_date))
                            break
            # 上穿
            elif get_price(date, 'close') > getBoll(date)[1]:
                # 看后三天有没有下穿
                for i in range(1, 4):
                    if sell_check_middle(date, date_calculate(date, i)):
                        # fourdays_later四天后，若收盘价仍低于中线卖出
                        fourdays_later = date_calculate(date, 4)
                        if get_price(fourdays_later, 'close') < getBoll(fourdays_later)[1]:
                            sell_signal.append(MyStruct(fourdays_later, 2, 'sell', middle_start_date))
                            middle_sell_list.append(MyStruct(fourdays_later, 2, 'sell', middle_start_date))
                            break
            # 初始化条件
            condition_flag = 1
            variety_rsi = 0.1
            middle_date = sorted(middle_buy_list + middle_sell_list, key=attrgetter("date"))
        return middle_buy_list, middle_sell_list, middle_date


# 买入条件：触及下沿线情况
# percent为用户指定的比例
def buy_check_touch_low(percent, end):
    # 股票最低价已经触及布林线下沿线
    flag1 = False
    # 在（1）成立的前提下，出现RSI-6 大于上一日指定比例时买入
    flag2 = False
    lowBoll = getBoll(end)[2]
    low = global_data.loc[global_data['trade_date'] == end].low.values[0]
    i = 0
    if lowBoll >= low:
        flag1 = True
    if flag1:
        while end is not None:
            nowRSI = getRSI(end)
            yesterdayRSI = getRSI(date_calculate(end, -1))
            if nowRSI > (yesterdayRSI * (1 + percent)):
                flag2 = True
                return flag2, i
            end = date_calculate(end, 1)
            i = i + 1
    return flag2, i - 1


# 买入条件：触及中界线情况
# 改写buy_check_touch_middle
def buy_check_touch_middle(end):
    # 股价从下往上越过中界线，即最高价大于中界线
    flag1 = False
    # 收盘为阳线，即收盘价高于开盘价
    flag2 = False
    midBoll = getBoll(end)[1]
    today_close = get_price(end, 'close')
    yes_close = get_price(date_calculate(end, -1), 'close')
    if yes_close < midBoll < today_close:
        flag1 = True
    if flag1:
        open = global_data.loc[global_data['trade_date'] == end].open.values[0]
        close = global_data.loc[global_data['trade_date'] == end].close.values[0]
        if close > open:
            flag2 = True
    return flag2


def buy_check_middle(last_date, date):
    # 股价从下往上越过中界线，即最高价大于中界线
    flag1 = False
    # 收盘为阳线，即收盘价高于开盘价
    flag2 = False
    midBoll = getBoll(date)[1]
    today_close = get_price(date, 'close')
    last_date_close = get_price(last_date, 'close')
    if last_date_close < midBoll < today_close:
        flag1 = True
    if flag1:
        open = global_data.loc[global_data['trade_date'] == date].open.values[0]
        close = global_data.loc[global_data['trade_date'] == date].close.values[0]
        if close > open:
            flag2 = True
    return flag2


def buy_check_condition_three(end, rsi_flag=1):
    global variety_rsi
    global condition_flag
    global condition_step
    day2 = date_calculate(end, 1)
    day3 = date_calculate(day2, 1)
    day4 = date_calculate(day3, 1)
    flag_day1 = buy_check_touch_middle(end)
    flag_day2 = check_middle(day2)
    flag_day3 = check_middle(day3)

    if condition_flag == 0:
        if flag_day1 and (flag_day2 or flag_day3) and compare_RSI(end, day2, day3, variety_rsi, rsi_flag):
            variety_rsi = variety_rsi * 1.5
            rsi_flag = rsi_flag * -1
            condition_step = condition_step + 1
            return buy_check_condition_three(day4, rsi_flag)
        condition_flag = 1
        variety_rsi = 0.1
    elif condition_flag == 1:
        if flag_day1:
            condition_flag = 0
            rsi_flag = rsi_flag * -1
            condition_step = condition_step + 1
            return buy_check_condition_three(day2, rsi_flag)
        variety_rsi = 0.1


# 单独列出做特殊处理
def check_condition_three(stock_code, isCharge, date, price, isWhole, type):
    global condition_step
    global transaction_signal
    global buy_signal, sell_signal
    flag = 1
    type_flag = 1
    if condition_step != 0:
        while condition_step > 0:
            if type == 'buy':
                if type_flag == 1:
                    buy_signal.append(date)
                    # print('buy 中线', date)
                    type = 0
                elif type_flag == 0:
                    sell_signal.append(date)
                    # print('sell buy中线条件', date)
                    type_flag = 1
                # 第一次成立从第二天开始
                if flag == 1:
                    date = date_calculate(date, 1)
                    flag = 0
                else:
                    date = date_calculate(date, 3)
                price = get_price(date, 'close')
                condition_step = condition_step - 1
            if type == 'sell':
                if type_flag == 1:
                    sell_signal.append(date)
                    # print('sell中线', date)
                    type = 0
                elif type_flag == 0:
                    buy_signal.append(date)
                    # print('buy sell中线条件', date)
                    type_flag = 1
                # 第一次成立从第二天开始
                if flag == 1:
                    date = date_calculate(date, 1)
                    flag = 0
                else:
                    date = date_calculate(date, 3)
                price = get_price(date, 'close')
                condition_step = condition_step - 1
        return date


# 对应文档特殊情况1
def buy_check_special(end):
    # 触及上沿线
    global special_buy_rsi
    flag1 = False
    flag2 = False
    date = end
    high = global_data.loc[global_data['trade_date'] == end].high.values[0]
    highBoll = getBoll(end)[0]
    if gol.get_value('special_buy_rsi') is not None:
        special_buy_rsi = gol.get_value('special_buy_rsi')
    if high >= highBoll:
        flag1 = True
    if flag1:
        # 向下循环
        while date is not None:
            date = date_calculate(date, 1)
            span_days = workdays(datetime.strptime(end, '%Y%m%d'), datetime.strptime(date, '%Y%m%d'))
            if date is not None:
                close = get_price(date, 'close')
                high = get_price(date, 'high')
                # 下降达到中界线
                if close <= getBoll(date)[1]:
                    break
                # 股价下一次触及上沿线
                if (high >= getBoll(date)[0]) & (span_days >= 3):
                    if (getRSI(date) <= 80) & (RSI_vary(date) > special_buy_rsi) & check_span_days(end, date, 'buy'):
                        buy_signal.append(MyStruct(date, 1, 'buy', date))
                        # print('buy 特1触高线', date)
                        flag2 = True
                    break
    return flag2


# RSI-6 下降到 20 以下
def buy_check_rsi():
    nowRSI = getRSI()
    if nowRSI < 20:
        return True
    return False


def is_buy_condition_three(date):
    global condition_step
    buy_check_condition_three(date)
    if condition_step != 0:
        return True
    return False


def buy(stock_code, isCharge, day, isWhole):
    global num
    global cost
    global all
    global principal
    global transaction_signal

    price = get_price(day, 'close')
    transaction_signal.append(1)
    # if (buy_check(percent, day)) & (principal > price * 100):
    cost = set_cost(day, principal, isWhole)
    # # 剩余仓位
    # cost = int(principal / (price * 100))
    # # 加仓2p-1
    # cost = ((0.7 + winning_percentage()) * 2 - 1) * cost
    # # 取满100股
    charge = 0
    if cost > 0:
        num += cost * 100
        principal -= cost * price * 100
        charge = 0
        if isCharge:
            charge = cost * price * 100 * 0.0003
            # 佣金最低5元
            if charge < 5:
                charge = 5
            principal -= charge
            all -= charge
        while principal < 0:
            cost -= 1
            num -= 100
            principal += price * 100
    if num > 0:
        sql = "INSERT IGNORE INTO backtest2(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
                                                    VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
              (stock_code, day, True, price, num, charge, False, all)
        db.commit_data(sql)
        print(day + " " + "buy: " + str(num) + "股 " + "价格：" + str(price) + " 剩余本金： " + str(
            principal) + " 总资产： " + str(all) + " 手续费： " + str(charge))


# 卖出条件：触及上沿线情况
# percent为用户指定的比例
def sell_check_touch_high(percent, end):
    # 股票最高价已经触及布林线上沿线
    flag1 = False
    # 在（1）成立的前提下，在出现RSI-6 小于上一日指定比例时卖出
    flag2 = False
    yes = date_calculate(end, -1)
    highBoll = getBoll(end)[0]
    high = global_data.loc[global_data['trade_date'] == end].high.values[0]
    i = 0
    if high >= highBoll:
        flag1 = True
    if flag1:
        while end is not None:
            nowRSI = getRSI(end)
            yesterdayRSI = getRSI(date_calculate(end, -1))
            # print(end,nowRSI,yesterdayRSI)
            if nowRSI < (yesterdayRSI * (1 - percent)):
                flag2 = True
                return flag2, i
            end = date_calculate(end, 1)
            i = i + 1
    return flag2, i - 1


# 卖出条件：触及中界线情况
def sell_check_touch_middle(end):
    # 股价从上往下越过中界线，即最低价小于中界线
    flag1 = False
    # 收盘为阴线，即收盘价低于开盘价
    flag2 = False
    midBoll = getBoll(end)[1]
    today_clsoe = get_price(end, 'close')
    yes_close = get_price(date_calculate(end, -1), 'close')
    if today_clsoe < midBoll < yes_close:
        flag1 = True
    if flag1:
        open = global_data.loc[global_data['trade_date'] == end].open.values[0]
        close = global_data.loc[global_data['trade_date'] == end].close.values[0]
        if close < open:
            flag2 = True
    return flag2


def sell_check_middle(last_date, date):
    # 股价从上往下越过中界线，即最低价小于中界线
    flag1 = False
    # 收盘为阴线，即收盘价低于开盘价
    flag2 = False
    midBoll = getBoll(date)[1]
    today_clsoe = get_price(date, 'close')
    last_date_close = get_price(last_date, 'close')
    if today_clsoe < midBoll < last_date_close:
        flag1 = True
    if flag1:
        open = global_data.loc[global_data['trade_date'] == date].open.values[0]
        close = global_data.loc[global_data['trade_date'] == date].close.values[0]
        if close < open:
            flag2 = True
    return flag2


def sell_check_condition_three(end, rsi_flag=-1):
    global variety_rsi
    global condition_flag
    global condition_step
    # 考虑交易日
    day2 = date_calculate(end, 1)
    day3 = date_calculate(day2, 1)
    day4 = date_calculate(day3, 1)
    flag_day1 = sell_check_touch_middle(end)
    flag_day2 = sell_check_touch_middle(day2)
    flag_day3 = sell_check_touch_middle(day3)

    if condition_flag == 0:
        if flag_day1 and (flag_day2 or flag_day3) and compare_RSI(end, day2, day3, variety_rsi, rsi_flag):
            variety_rsi = variety_rsi * 1.5
            rsi_flag = rsi_flag * -1
            condition_step = condition_step + 1
            return sell_check_condition_three(day4, rsi_flag) * -1
        condition_flag = 1
        variety_rsi = 0.1
        # print('sell',condition_step)
        return 1
    elif condition_flag == 1:
        if flag_day1:
            condition_flag = 0
            rsi_flag = rsi_flag * -1
            # variety_rsi = variety_rsi * 1.5
            condition_step = condition_step + 1
            return sell_check_condition_three(day2, rsi_flag) * -1
        variety_rsi = 0.1
        # print('sell',condition_step)
        return 1


# 对应文档特殊情况2
def sell_check_special(end):
    # 触及下沿线
    global special_sell_rsi
    flag1 = False

    flag2 = False
    date = end
    low = global_data.loc[global_data['trade_date'] == end].low.values[0]
    lowBoll = getBoll(end)[2]
    if gol.get_value('special_sell_rsi') is not None:
        special_sell_rsi = gol.get_value('special_sell_rsi')
    if low <= lowBoll:
        flag1 = True
    if flag1:
        # 回溯前30天
        while date is not None:
            date = date_calculate(date, 1)
            next_date = date_calculate(date, 1)
            if date is not None:
                span_days = workdays(datetime.strptime(end, '%Y%m%d'), datetime.strptime(date, '%Y%m%d'))
                close = get_price(date, 'close')
                low = get_price(date, 'low')
                # 上升达到中界线
                if close >= getBoll(date)[1] or low <= getBoll(date)[2]:
                    break
                # 股价下一次触及下沿线
                if (low <= getBoll(date)[2]) & (span_days >= 3):
                    if check_span_days(end, date, 'sell'):
                        if (getRSI(date) >= 20) & (RSI_vary(date) < special_sell_rsi * -1):
                            sell_signal.append(MyStruct(date, 1, 'sell', date))
                            # print('sell 特2触低线', date)
                            flag2 = True
                            break
                        elif get_price(next_date, 'low') < getBoll(next_date)[2]:
                            sell_signal.append(MyStruct(next_date, 1, 'sell', next_date))
                            break
    return flag2


# 特殊情况3
def check_special(end):
    highBoll = getBoll(end)[0]
    high = global_data.loc[global_data['trade_date'] == end].high.values[0]
    lowBoll = getBoll(end)[2]
    low = global_data.loc[global_data['trade_date'] == end].low.values[0]
    rsi = getRSI(end)
    if rsi > 80:
        sell_signal.append(MyStruct(end, 1, 'sell', end))
        # print('sell rsi大于80', end)
        return -1
    if rsi < 20:
        buy_signal.append(MyStruct(end, 1, 'buy', end))
        # print('buy rsi小于20', end)
        return 1
    if high >= highBoll and lowBoll >= low:
        open = global_data.loc[global_data['trade_date'] == end].open.values[0]
        close = global_data.loc[global_data['trade_date'] == end].close.values[0]
        # 阴线收盘
        if open > close:
            sell_signal.append(MyStruct(end, 1, 'sell', end))
            # print('sell 阴线收盘', end)
            return -1
        # 阳线收盘
        if open < close:
            buy_signal.append(MyStruct(end, 1, 'buy', end))
            # print('buy 阳线收盘', end)
            return 1
    # 特数情况rsi大于80或rsi小于20
    return 0


# RSI-6 超过 80
def buy_check_rsi():
    nowRSI = getRSI()[-1]
    if nowRSI > 80:
        return True
    return False


def is_sell_condition_three(date):
    global condition_step
    sell_check_condition_three(date)
    if condition_step != 0:
        return True
    return False


def buy_check(percent, end):
    if check_special(end) == 1:
        return True
    if buy_check_special(end):
        return True
    # 如果买入条件1与卖出条件2同时出现，先执行卖出条件2；
    return False


def sell_check(percent, end):
    if check_special(end) == -1:
        return True
    if sell_check_special(end):
        return True
    # 如果买入条件2与卖出条件1同时出现，先执行买入条件2；
    return False


def sell(stock_code, isCharge, day):
    global num
    global cost
    global all
    global principal
    global transaction_signal
    # if sell_check(percent, day) and num > 0:
    price = get_price(day, 'close')
    transaction_signal.append(-1)
    principal += num * price
    all = principal
    charge = 0
    stamp_tax = 0
    if isCharge:
        charge = cost * price * 100 * 0.0003
        # 佣金最低5元
        if charge < 5:
            charge = 5
        # 印花税
        stamp_tax = cost * price * 100 * 0.001
        charge += stamp_tax
        principal -= charge
        all -= charge
    sql = "INSERT IGNORE INTO backtest2(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
                                                                VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
          (stock_code, day, False, price, num, charge, False, all)
    db.commit_data(sql)
    print(day + " " + "sell: " + str(num) + "股 " + "价格：" + str(price) + " 剩余本金： " + str(
        principal) + " 总资产： " + str(all) + " 佣金： " + str(charge) + " 印花税： " + str(stamp_tax))
    num = 0


# 止损
def stop_loss(stock_code, isCharge, day):
    global num
    global cost
    global all
    global principal
    global begin
    global transaction_signal

    price = get_price(day, 'close')
    transaction_signal.append(-1)
    print("强制止损")
    principal += num * price
    all = principal
    charge = 0
    stamp_tax = 0
    if isCharge:
        charge = cost * price * 100 * 0.0003
        # 佣金最低5元
        if charge < 5:
            charge = 5
        # 印花税
        stamp_tax = cost * price * 100 * 0.001
        charge += stamp_tax
        principal -= charge
        all -= charge
    sql = "INSERT IGNORE INTO backtest2(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
                                                                            VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
          (stock_code, day, False, price, num, charge, True, all)
    db.commit_data(sql)
    print(day + " " + "sell: " + str(num) + "股 " + "价格：" + str(price) + " 剩余本金： " + str(
        principal) + " 总资产： " + str(all) + " 佣金： " + str(charge) + " 印花税： " + str(stamp_tax))
    num = 0


def check_stop(stoploss):
    buy_list = sorted(buy_signal, key=attrgetter("date"))
    buy_date = [item.date for item in buy_list]
    buy_date = sorted(list(set(buy_date)))
    stop_signal = []
    while len(buy_date) > 1:
        start = buy_date[0]
        end = buy_date[1]
        buy_price = get_price(start, 'close')
        while start < end:
            start = date_calculate(start, 1)
            now_price = get_price(start, 'close')
            if now_price < (1 - stoploss) * buy_price:
                stop_signal.append(MyStruct(start, 1, 'stop', buy_date[0]))
                buy_date.pop(0)
                break
        buy_date.pop(0)
    last_date = buy_date[0]
    if last_date < gol_end and len(buy_date) == 1:
        buy_price = get_price(last_date, 'close')
        while last_date < gol_end:
            last_date = date_calculate(last_date,1)
            now_price = get_price(last_date, 'close')
            if now_price < (1 - stoploss) * buy_price:
                stop_signal.append(MyStruct(last_date, 1, 'stop', buy_date[0]))
                break
    return stop_signal



# 从buy_signal和sell_signal从匹配交易日期
def transaction(stock_code, stoploss, isCharge, isWhole):
    global buy_signal, sell_signal
    # 去重
    buy_signal = np.unique(sorted(buy_signal))
    sell_signal = np.unique(sorted(sell_signal))
    print('全部买点', buy_signal)
    print('全部卖点', sell_signal)
    trans_flag = 1
    while len(buy_signal) != 0:
        buy_date = buy_signal[0]
        buy_price = get_price(buy_date, 'close')
        if len(sell_signal) != 0:
            sell_date = sell_signal[0]
            sell_price = get_price(sell_date, 'close')
            if (buy_date < sell_date) & trans_flag == 1:
                buy(stock_code, isCharge, buy_date, buy_price, isWhole)
                if not check_stop(buy_date, sell_date, stoploss)[0]:
                    sell(stock_code, isCharge, sell_date, sell_price)
                    last_sell_date = sell_signal[0]
                    sell_signal = np.delete(sell_signal, 0)
                else:
                    sell_date = check_stop(buy_date, sell_date, stoploss)[1]
                    print("stop", sell_date)
                    sell(stock_code, isCharge, sell_date, sell_price)
                buy_signal = np.delete(buy_signal, 0)
                trans_flag = 0
            elif buy_date >= sell_date:
                sell_signal = np.delete(sell_signal, 0)
            elif buy_date <= last_sell_date:
                buy_signal = np.delete(buy_signal, 0)
            elif (buy_date > last_sell_date) & (buy_date < sell_date) & trans_flag == 0:
                buy(stock_code, isCharge, buy_date, buy_price, isWhole)
                if not check_stop(buy_date, sell_date, stoploss)[0]:
                    sell(stock_code, isCharge, sell_date, sell_price)
                    last_sell_date = sell_signal[0]
                    sell_signal = np.delete(sell_signal, 0)
                else:
                    sell_date = check_stop(buy_date, sell_date, stoploss)[1]
                    print("stop", sell_date)
                    sell(stock_code, isCharge, sell_date, sell_price)
                buy_signal = np.delete(buy_signal, 0)
        else:
            if buy_date > last_sell_date:
                buy(stock_code, isCharge, buy_date, buy_price, isWhole)
                break
            else:
                buy_signal = np.delete(buy_signal, 0)


# 参数从左到右依次是初始本金，股票代码，RSI-6变化比率，止损比率，回测周期，是否计算手续费
def trading_strategy2_whole(principal, stock_code, percent, stoploss, span, isCharge):
    global history_240
    # 取数起始日期
    start = history_240['trade_date'][len(history_240) - 1]
    start = history_240.loc[history_240['trade_date'] == start].index[0]
    # 回测日期列表
    day = []
    try:
        # 此处多计入不做交易的周六 日
        day = history_240['trade_date'][-(span):]
        print(day)
    except Exception as e:
        print(e)
    # 仓位，单位是股数
    num = 0
    # 总资产数
    all = principal
    # 起始资金数，用于判断是否需要强制止损
    begin = principal
    db = database_connection.MySQLDb()
    for d in day:
        end = history_240.loc[history_240['trade_date'] == d].index[0]
        global history_data
        history_data = history_240.loc[start:end]
        history_data = history_data.reset_index(drop=True)
        history_data = history_data.iloc[::-1]
        history_data = history_data.reset_index(drop=True)
        history_data = history_data.sort_index(ascending=False)
        global now_data
        now_data = history_240[history_240['trade_date'] == d]
        price = now_data['close'].values[0]
        # 单笔交易至少有100股
        if buy_check(percent) and principal > price * 100:
            cost = int(principal / (price * 100))
            num += cost * 100
            principal -= cost * price * 100
            charge = 0
            if isCharge:
                charge = cost * price * 100 * 0.0003
                # 佣金最低5元
                if charge < 5:
                    charge = 5
                principal -= charge
                all -= charge
                while principal < 0:
                    cost -= 1
                    num -= 100
                    principal += price * 100
            if num > 0:
                sql = "INSERT IGNORE INTO backtest2(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
                                                            VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
                      (stock_code, d, True, price, cost * 100, charge, False, all)
                db.commit_data(sql)
                print(d + " " + "buy: " + str(num) + "股 " + "价格：" + str(price) + " 剩余本金： " + str(
                    principal) + " 总资产： " + str(all) + " 手续费： " + str(charge))
        # 确保有可卖出的股数
        if sell_check(percent) and num > 0:
            principal += num * price
            all = principal
            charge = 0
            stamp_tax = 0
            cost = int(principal / (price * 100))
            if isCharge:
                charge = cost * price * 100 * 0.0003
                # 佣金最低5元
                if charge < 5:
                    charge = 5
                # 印花税
                stamp_tax = cost * price * 100 * 0.001
                charge += stamp_tax
                principal -= charge
                all -= charge
            sql = "INSERT IGNORE INTO backtest2(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
                                                                    VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
                  (stock_code, d, False, price, num, charge, False, all)
            db.commit_data(sql)
            print(d + " " + "sell: " + str(num) + "股 " + "价格：" + str(price) + " 剩余本金： " + str(
                principal) + " 总资产： " + str(all) + " 佣金： " + str(charge) + " 印花税： " + str(stamp_tax))
            num = 0
        # 强制止损
        if num != 0 and all < begin and abs(all - principal - begin) >= stoploss * (all - principal):
            print("强制止损")
            principal += num * price
            all = principal
            charge = 0
            stamp_tax = 0
            if isCharge:
                charge = cost * price * 100 * 0.0003
                # 佣金最低5元
                if charge < 5:
                    charge = 5
                # 印花税
                stamp_tax = cost * price * 100 * 0.001
                charge += stamp_tax
                principal -= charge
                all -= charge
            sql = "INSERT IGNORE INTO backtest2(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
                                                                                VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
                  (stock_code, d, False, price, num, charge, False, all)
            db.commit_data(sql)
            print(d + " " + "sell: " + str(num) + "股 " + "价格：" + str(price) + " 剩余本金： " + str(
                principal) + " 总资产： " + str(all) + " 佣金： " + str(charge) + " 印花税： " + str(stamp_tax))
            num = 0
    print("共计： " + str(span) + "个交易日")
    return all


def winning_percentage():
    data = history_240['close']
    # 5日均线
    five = data.ewm(span=5, adjust=False, min_periods=5).mean().loc[0]
    five_before = data.ewm(span=5, adjust=False, min_periods=5).mean().loc[1]
    # 10日均线
    ten = data.ewm(span=10, adjust=False, min_periods=10).mean().loc[0]
    ten_before = data.ewm(span=10, adjust=False, min_periods=10).mean().loc[1]
    # 20日均线
    twenty = data.ewm(span=20, adjust=False, min_periods=20).mean().loc[0]
    twenty_before = data.ewm(span=20, adjust=False, min_periods=20).mean().loc[1]
    # 40日均线
    forty = data.ewm(span=40, adjust=False, min_periods=40).mean().loc[0]
    forty_before = data.ewm(span=40, adjust=False, min_periods=40).mean().loc[1]
    # 60日均线
    sixty = data.ewm(span=60, adjust=False, min_periods=60).mean().loc[0]
    sixty_before = data.ewm(span=60, adjust=False, min_periods=60).mean().loc[1]
    # 120日均线
    one_hundred_and_twenty = data.ewm(span=120, adjust=False, min_periods=120).mean().loc[0]
    one_hundred_and_twenty_before = data.ewm(span=120, adjust=False, min_periods=120).mean().loc[1]
    # 240日均线
    two_hundred_and_forty = data.ewm(span=240, adjust=False, min_periods=240).mean().loc[0]
    cnt = 0
    if five > ten and five - five_before > 0:
        cnt += 1
    if ten > twenty and five - five_before > 0 and ten - ten_before > 0:
        cnt += 1
    if twenty > forty and five - five_before > 0 and ten - ten_before > 0 and twenty - twenty_before > 0:
        cnt += 1
    if forty > sixty and five - five_before > 0 and ten - ten_before > 0 and twenty - twenty_before > 0 and forty - forty_before > 0:
        cnt += 1
    if sixty > one_hundred_and_twenty and five - five_before > 0 and ten - ten_before > 0 and twenty - twenty_before > 0 and forty - forty_before > 0 and sixty - sixty_before > 0:
        cnt += 1
    if two_hundred_and_forty > one_hundred_and_twenty and five - five_before > 0 and ten - ten_before > 0 and twenty - twenty_before > 0 and forty - forty_before > 0 and sixty - sixty_before > 0 and one_hundred_and_twenty - one_hundred_and_twenty_before > 0:
        cnt += 1
    # 每满足一项条件胜率就增5%
    return cnt * 0.05


# 获取对应中线条件日期长度
def get_middle_len(date):
    tran = []
    for item in middle_date:
        if item.time == date and item.priority == 2:
            tran.append(item)
    return len(tran)

# 获取中线条件中日期的位置
def get_middle_position(date, time):
    tran = []
    for item in middle_date:
        if item.time == time and item.priority == 2:
            tran.append(item.date)
    return tran.index(date)

def new_trans(stock_code, stoploss, isCharge, isWhole):
    global can_middle_flag, condition_step, middle_time
    # 止损日期
    stop_signal = check_stop(stoploss)
    trans = buy_signal + sell_signal + stop_signal
    # shanchu
    trans = list(set(trans))
    trans = sorted(trans, key=attrgetter("date"))
    check_stop(stoploss)
    print(trans)
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
                        trans.pop(0)
                        continue
                elif item.type == 'notbuy' and item.time == middle_time:
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




# 参数从左到右依次是初始本金，股票代码，RSI-6变化比率，止损比率，回测周期，是否计算手续费
def trading_strategy2_position(principa, stock_code, percent, stoploss, span, isCharge, isWhole, transdate):
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
    # 记录所有传中线的日期
    # for date in day:
    # if get_price(date_calculate(date, -1), 'close') > getBoll(date)[1] > get_price(date, 'close'):
    #     all_middle_sell_list.append(date)
    # if get_price(date_calculate(date, -1), 'close') < getBoll(date)[1] < get_price(date, 'close'):
    #     all_middle_buy_list.append(date)
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
            # 哪个优先级高
            # 怎么将中线条件插入？
            # check_middle(d)
            # if is_buy_condition_three(d):
            #     check_condition_three(stock_code, isCharge, d, price, isWhole, 'buy')
            # print('buy3 中线', d)
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
            # if is_sell_condition_three(d):
            #     # print('sell3 中线', d)
            #     check_condition_three(stock_code, isCharge, d, price, isWhole, 'sell')
        # 强制止损
        if num != 0 and all < begin and abs(all - principal - begin) >= stoploss * (all - principal):
            stop_loss(stock_code, isCharge, d)
    # transaction(stock_code, stoploss, isCharge, isWhole)
    new_trans(stock_code, stoploss, isCharge, isWhole)

    print("共计： " + str(span) + "个交易日")
    print('---------------------------------------------------------------------------------------------------------')
    print('---------------------------------------------------------------------------------------------------------')
    return all


def backtest2(span, stock_code, principal, percent, stoploss, isCharge, isWhole):
    day = date.today()  # 当前日期
    now = datetime.now()
    delta = timedelta(days=240 * 1.5 + 100)  # 采取时间差*1.5+100的方式确保能获得足够的交易日
    n_days_forward = now - delta  # 当前日期向前推n天的时间
    start_day = n_days_forward.strftime('%Y%m%d')
    end_day = day.strftime('%Y%m%d')
    df = []
    while True:
        try:
            df = pro.daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
            break
        except:
            continue
    df = df.sort_values(by='trade_date', ascending=True)
    global history_240
    history_240 = df
    global history_data
    history_data = df
    db = database_connection.MySQLDb()
    db.clean_table("TRUNCATE TABLE `backtest2`;")
    if isWhole:
        return trading_strategy2_whole(principal, stock_code, percent, stoploss, span, isCharge)
    else:
        return trading_strategy2_position(principal, stock_code, percent, stoploss, span, isCharge)


def date_backtest2(start_day, end_day, stock_code, principal, percent, stoploss, isCharge, isWhole):
    global gol_start, gol_end
    start = datetime(int(start_day[0:4]), int(start_day[4:6]), int(start_day[6:8]))
    end = datetime(int(end_day[0:4]), int(end_day[4:6]), int(end_day[6:8]))
    startbak = start_day
    endbak = end_day
    span = workdays(start, end)
    day = end
    # delta = timedelta(days=30)
    delta = timedelta(days=240 * 1.5 + 100)  # 采取时间差*1.5+100的方式确保能获得足够的交易日
    n_days_forward = day - delta  # 当前日期向前推n天的时间
    day = day + timedelta(days=15)
    start_day = n_days_forward.strftime('%Y%m%d')
    end_day = day.strftime('%Y%m%d')
    # 往后推半个月 确保能取满周期
    set_info(start_day, end_day, stock_code)
    transdate = used_date(startbak, endbak)
    gol_start = startbak
    gol_end = endbak
    print(start, end, span, day, delta, n_days_forward, start_day, end_day, stock_code)
    db = database_connection.MySQLDb()
    db.clean_table("TRUNCATE TABLE `backtest2`;")
    return trading_strategy2_position(principal, stock_code, percent, stoploss, span, isCharge, isWhole, transdate)


# 调用示例：
# backtest2(30, '300917.SZ', 9999999, 0.1, 0.1, False, True)
# date_backtest2('20220321', '20220613', '600256.SH', 9999999, 0.1, 0.3, False, True)


# date_backtest2('20220325', '20220614', '600073.SH', 9999999, 0.1, 0.3, False, True)
# clear()
# date_backtest2('20220321', '20220613', '600256.SH', 9999999, 0.1, 0.3, False, True)
# clear()


# date_backtest2('20220318', '20220524', '600546.SH', 9999999, 0.1, 0.3, False, True)
# clear()
# date_backtest2('20220408', '20220613', '601069.SH', 9999999, 0.1, 0.3, False, True)
# clear()
# date_backtest2('20220310', '20220609', '516950.SH', 9999999, 0.1, 0.3, False, True)
# date_backtest2('20220427', '20220609', '512690.SH', 9999999, 0.1, 0.3, False, True)
# clear()
# date_backtest2('20220316', '20220607', '601009.SH', 9999999, 0.1, 0.3, False, True)
# clear()
# date_backtest2('20220421', '20220523', '600277.SH', 9999999, 0.1, 0.3, False, True)
# clear()
# date_backtest2('20220513', '20220527', '300917.SH', 9999999, 0.1, 0.3, False, True)
# clear()
# date_backtest2('20220325', '20220614', '600073.SH', 9999999, 0.1, 0.3, False, True)


date_backtest2('20220427', '20220609', '512690.SH', 9999999, 0.1, 0.3, False, True)

# set_info('20220220', '20220609', '512690.SH')
# check_middle('20220516')
# for item in middle_buy_list:
#     print(item.date,item.type)
# print(middle_buy_list)
# print(middle_sell_list)
# print(not_buy_date)
# print(not_sell_date)
