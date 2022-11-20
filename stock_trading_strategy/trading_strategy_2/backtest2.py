import math
import sys
import pandas as pd
import pymysql
import tushare as ts
import talib as ta
from datetime import date, datetime, timedelta, time
from chinese_calendar import is_workday
from data_modules import database_connection

pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')
sys.path.append("../data_modules/database_connection.py")

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
# 对应买卖条件中第三条变化的RSI
variety_rsi = 0.1
# 记录条件三的日期
history_condition = pd.DataFrame
# 记录条件三检测日期
condition_date = date
# 开始日期
start_day = ''
# 结束日期
end_day = ''
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

# 显示所有行
pd.set_option('display.max_rows', 1000)
# 显示所有列
pd.set_option('display.max_columns', 1000)


def set_info(start, end, stock):
    global start_day
    global end_day
    global stock_code
    start_day = start
    end_day = end
    stock_code = stock
    return


def setdata(start_day, end_day, stock_code):
    while True:
        try:
            df = pro.daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
            global now_data
            now_data = df.loc[0]
            break
        except:
            continue
    df = df.sort_values(by='trade_date', ascending=True)
    #
    # global history_240
    # history_240 = df
    # global history_data
    # history_data = df
    return df


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
        if is_workday(start):
            counts += 1
        start += timedelta(days=1)
    return counts


# 日期前推 后推
def date_calculate(date, days):
    start = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
    delta = timedelta(days=days)  # 采取时间差*1.5+100的方式确保能获得足够的交易日
    n_days_forward = start + delta  # 当前日期向前推n天的时间
    start_day = n_days_forward.strftime('%Y%m%d')
    return start_day


# 比较三天之内每前后两天的RSI
def compare_RSI(day1, day2, day3, baseline, flag):
    rsi_day1 = getRSI(day1)[-1]
    rsi_day2 = getRSI(day2)[-1]
    rsi_day3 = getRSI(day3)[-1]
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
    rsi_day1 = getRSI(day1)[-1]
    rsi_day2 = getRSI(day2)[-1]
    rsi_day3 = getRSI(day3)[-1]
    if rsi_day2 > (1 + baseline) * rsi_day1 or rsi_day3 > (1 + baseline) * rsi_day2:
        return True
    else:
        return False


def become_workday(date):
    while True:
        if not is_workday(datetime.strptime(date, '%Y%m%d')):
            date = date_calculate(date, 1)
        else:
            break
    return date

def become_workday_yes(date):
    while True:
        if not is_workday(datetime.strptime(date, '%Y%m%d')):
            date = date_calculate(date, -1)
        else:
            break
    return date


def set_cost(principal):
    price = now_data['close']
    cost = int(principal / (price * 100))
    # 加仓2p-1
    cost = ((0.7 + winning_percentage()) * 2 - 1) * cost
    # 取满100股
    cost = math.floor(cost / 100) * 100
    return cost


def load_historical_data(stock_code, start_day, end_day):
    df = pro.daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
    global yesterday_data
    yesterday_data = df.loc[1]
    global now_data
    now_data = df.loc[0]
    df = df.sort_values(by='trade_date', ascending=True)
    global history_data
    history_data = df
    return


# def getBoll():
#     global history_data
#     df = history_data
#     high, middle, low = ta.BBANDS(
#         df['close'].values,
#         timeperiod=20,
#         # 与平均值的无偏倚标准差的数量
#         nbdevup=2,
#         nbdevdn=2,
#         # 移动平均线类型：0为简单移动平均线
#         matype=0)
#     # high: getBoll()[0]
#     return high, middle, low

# 改写getBoll()
def getBoll(date=end_day):
    # global history_data
    df = setdata(start_day, date, stock_code)
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


# def getRSI():
#     global history_data
#     df = history_data
#     # 6日rsi
#     rsi = ta.RSI(df['close'].values, timeperiod=6)
#     return rsi

# 改写getRSI()
def getRSI(date=end_day):
    # if date is pd.DataFrame:
    #     df = history_data
    # else:
    #     df = date
    df = setdata(start_day, date, stock_code)
    # global history_data
    # df = history_data
    # 6日rsi
    rsi = ta.RSI(df['close'].values, timeperiod=6)
    return rsi


# 买入条件：触及下沿线情况
# percent为用户指定的比例
def buy_check_touch_low(percent, end):
    # 股票最低价已经触及布林线下沿线
    flag1 = False
    # 在（1）成立的前提下，出现RSI-6 大于上一日指定比例时买入
    flag2 = False
    lowBoll = getBoll(end)[2][-1]
    low = now_data['low']
    if lowBoll >= low:
        flag1 = True
    if flag1:
        nowRSI = getRSI(end)[-1]
        yesterdayRSI = getRSI(end)[-2]
        if nowRSI > (yesterdayRSI * (1 + percent)):
            flag2 = True
    return flag2


# 买入条件：触及中界线情况
# def buy_check_touch_middle():
#     # 股价从下往上越过中界线，即最高价大于中界线
#     flag1 = False
#     # 收盘为阳线，即收盘价高于开盘价
#     flag2 = False
#
#     midBoll = getBoll()[1][-1]
#     high = now_data['high'].values[0]
#     # 改1
#     low = now_data['low'].values[0]
#     if (high > midBoll) & (midBoll > low):
#         flag1 = True
#     if flag1:
#         open = now_data['open'].values[0]
#         close = now_data['close'].values[0]
#         if close > open:
#             flag2 = True
#     return flag2

# 改写buy_check_touch_middle
def buy_check_touch_middle(end):
    # 股价从下往上越过中界线，即最高价大于中界线
    flag1 = False
    # 收盘为阳线，即收盘价高于开盘价
    flag2 = False
    midBoll = getBoll(end)[1][-1]
    high = now_data['high']
    # 改1
    low = now_data['low']
    if (high > midBoll) & (midBoll > low):
        flag1 = True
    if flag1:
        open = now_data['open']
        close = now_data['close']
        if close > open:
            flag2 = True
    # print('buy_check_touch_middle')
    return flag2


def buy_check_condition_three(end, rsi_flag=1):
    global variety_rsi
    global condition_flag
    global condition_step
    day2 = become_workday(date_calculate(end, 1))
    day3 = become_workday(date_calculate(day2, 1))
    day4 = become_workday(date_calculate(day3, 1))
    # day2 = date_calculate(end, 1)
    # 考虑工作日
    # while True:
    #     if not is_workday(datetime.strptime(day2, '%Y%m%d')):
    #         day2 = date_calculate(day2, 1)
    #     break
    # day3 = date_calculate(day2, 1)
    # while True:
    #     if not is_workday(datetime.strptime(day3, '%Y%m%d')):
    #         day3 = date_calculate(day3, 1)
    #     break
    # day4 = date_calculate(day3, 1)
    # while True:
    #     if not is_workday(datetime.strptime(day4, '%Y%m%d')):
    #         day4 = date_calculate(day4, 1)
    #     break
    flag_day1 = buy_check_touch_middle(end)
    flag_day2 = buy_check_touch_middle(day2)
    flag_day3 = buy_check_touch_middle(day3)

    # test
    # print(end, day2, day3)
    # print(flag_day1, flag_day2, flag_day3, compare_RSI(end, day2, day3, variety_rsi, rsi_flag))
    # print('___________')
    # print(rsi_flag)
    # print('___________')
    # print(variety_rsi)
    # print('___________________________')

    if condition_flag == 0:
        if flag_day1 and (flag_day2 or flag_day3) and compare_RSI(end, day2, day3, variety_rsi, rsi_flag):
            variety_rsi = variety_rsi * 1.5
            rsi_flag = rsi_flag * -1
            condition_step = condition_step + 1
            return buy_check_condition_three(day4, rsi_flag) * -1
        condition_flag = 1
        variety_rsi = 0.1
        # print(condition_step)
        return 1
    elif condition_flag == 1:
        if flag_day1 and (flag_day2 or flag_day3):
            condition_flag = 0
            rsi_flag = rsi_flag * -1
            # variety_rsi = variety_rsi * 1.5
            condition_step = condition_step + 1
            return buy_check_condition_three(day4, rsi_flag) * -1
        variety_rsi = 0.1
        # print(condition_step)
        return 1


# 单独列出做特殊处理
def check_buy_condition_three(stock_code, isCharge, date, price):
    global condition_step
    global transaction_signal
    var = 1
    #sell_check_condition_three(date)
    step = condition_step
    if condition_step != 0:
        while condition_step > 0:
            if len(transaction_signal) == 0 or transaction_signal[-1] == -1:
                buy(stock_code, isCharge, date, price)
                # transaction_signal.append(1)
            elif transaction_signal[-1] == 1:
                sell(stock_code, isCharge, date, price)
                # transaction_signal.append(-1)
            date = become_workday(date_calculate(date,3))
            price = history_240[history_240['trade_date'] == date]['close'].values[-1]
            condition_step = condition_step - 1
        #要考虑其中包含休息日的可能
        # while var <= step *3:
        # #date是下个周期开始日期
        #     date = become_workday(date_calculate(date,1))
        #     var = var +1
        condition_step = 0
        return date

# 对应文档特殊情况1
def buy_check_special(end):
    # 触及上沿线
    flag1 = False

    flag2 = False

    high = now_data['high']
    highBoll = getBoll(end)[0][-1]
    if high >= highBoll:
        flag1 = True
    if flag1:
        # 回溯前30天
        # history_30 = history_data[-30:]
        for i in range(0, 30):
            close = history_data[-30:].loc[i]['close']
            # 下降达到中界线
            if close <= getBoll(end)[1][-(1 + i)]:
                break
            high = history_data[-30:].loc[i]['high']
            # 股价上一次触及上沿线
            if high >= getBoll(end)[0][-(1 + i)]:
                if i > 3:
                    flag2 = True
                break
    # print('buy_check_special')
    return flag2


# RSI-6 下降到 20 以下
def buy_check_rsi():
    nowRSI = getRSI()[-1]
    if nowRSI < 20:
        return True
    return False

def is_buy_condition_three(date):
    global condition_step
    buy_check_condition_three(date)
    if condition_step != 0:
        return True
    return False

def buy(stock_code, isCharge, day, price):
    global num
    global cost
    global all
    global principal
    global transaction_signal

    transaction_signal.append(1)
    # if (buy_check(percent, day)) & (principal > price * 100):
    cost = set_cost(principal)
    # # 剩余仓位
    # cost = int(principal / (price * 100))
    # # 加仓2p-1
    # cost = ((0.7 + winning_percentage()) * 2 - 1) * cost
    # # 取满100股
    # cost = math.floor(cost / 100) * 100
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

    highBoll = getBoll(end)[0][-1]
    high = now_data['high']
    if high >= highBoll:
        flag1 = True
    if flag1:
        nowRSI = getRSI(end)[-1]
        yesterdayRSI = getRSI(end)[-2]
        if nowRSI < (yesterdayRSI * (1 - percent)):
            flag2 = True
    return flag2


# 卖出条件：触及中界线情况
def sell_check_touch_middle(end):
    # 股价从上往下越过中界线，即最低价小于中界线
    flag1 = False
    # 收盘为阴线，即收盘价低于开盘价
    flag2 = False

    midBoll = getBoll(end)[1][-1]
    low = now_data['low']
    # gai2
    high = now_data['high']
    if low < midBoll < high:
        flag1 = True
    if flag1:
        open = now_data['open']
        close = now_data['close']
        if close < open:
            flag2 = True
    # print('sell_check_touch_middle')
    return flag2


def sell_check_condition_three(end, rsi_flag=-1):
    global variety_rsi
    global condition_flag
    global condition_step
    day2 = become_workday(date_calculate(end, 1))
    day3 = become_workday(date_calculate(day2, 1))
    day4 = become_workday(date_calculate(day3, 1))
    # 考虑工作日
    # while True:
    #     if not is_workday(datetime.strptime(day2, '%Y%m%d')):
    #         day2 = date_calculate(day2, 1)
    #     break
    # day3 = date_calculate(day2, 1)
    # while True:
    #     if not is_workday(datetime.strptime(day3, '%Y%m%d')):
    #         day3 = date_calculate(day3, 1)
    #     break
    # day4 = date_calculate(day3, 1)
    # while True:
    #     if not is_workday(datetime.strptime(day4, '%Y%m%d')):
    #         day4 = date_calculate(day4, 1)
    #     break
    flag_day1 = sell_check_touch_middle(end)
    flag_day2 = sell_check_touch_middle(day2)
    flag_day3 = sell_check_touch_middle(day3)

    # test
    # print(end, day2, day3)
    # print(flag_day1, flag_day2, flag_day3, compare_RSI(end, day2, day3, variety_rsi, rsi_flag))
    # print(rsi_flag)
    # print('___________________________')

    if condition_flag == 0:
        if flag_day1 and (flag_day2 or flag_day3) and compare_RSI(end, day2, day3, variety_rsi, rsi_flag):
            variety_rsi = variety_rsi * 1.5
            rsi_flag = rsi_flag * -1
            condition_step = condition_step + 1
            return sell_check_condition_three(day4, rsi_flag) * -1
        condition_flag = 1
        variety_rsi = 0.1
        # print(condition_step)
        return 1
    elif condition_flag == 1:
        if flag_day1 and (flag_day2 or flag_day3):
            condition_flag = 0
            rsi_flag = rsi_flag * -1
            # variety_rsi = variety_rsi * 1.5
            condition_step = condition_step + 1
            return sell_check_condition_three(day4, rsi_flag) * -1
        variety_rsi = 0.1
        # print(condition_step)
        return 1


# 同样特殊处理
def check_sell_condition_three(date):
    global condition_step
    global transaction_signal
    var = 1
    sell_check_condition_three(date)
    step = condition_step
    if condition_step != 0:
        while condition_step > 0:
            if len(transaction_signal) == 0 or transaction_signal[-1] == -1:
                # buy
                transaction_signal.append(1)
            elif transaction_signal[-1] == 1:
                # sell
                transaction_signal.append(-1)
            condition_step = condition_step - 1
        #要考虑其中包含休息日的可能
        while var <= step *3:
        #date是下个周期开始日期
            date = become_workday(date_calculate(date,1))
            var = var +1
            condition_step = 0
        return date

# 对应文档特殊情况2
def sell_check_special(end):
    # 触及下沿线
    flag1 = False

    flag2 = False

    low = now_data['low']
    lowBoll = getBoll(end)[2][-1]
    if low <= lowBoll:
        flag1 = True
    if flag1:
        # 回溯前30天
        for i in range(0, 30):
            close = history_data[-30:].loc[i]['close']
            # 上升达到中界线
            if close >= getBoll(end)[1][-(1 + i)]:
                break
            low = history_data[-30:].loc[i]['low']
            # 股价上一次触及下沿线
            if low <= getBoll(end)[2][-(1 + i)]:
                if i > 3:
                    flag2 = True
                break

    return flag2


# 特殊情况3
def check_special(end):
    highBoll = getBoll(end)[0][-1]
    high = now_data['high']
    lowBoll = getBoll(end)[2][-1]
    low = now_data['low']
    if high >= highBoll and lowBoll >= low:
        open = now_data['open']
        close = now_data['close']
        # 阴线收盘
        if open > close:
            return -1
        # 阳线收盘
        if open < close:
            return 1
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
    # if buy_check_touch_low(percent, end) and sell_check_touch_middle(end):
    #     return False
    # if buy_check_touch_low(percent, end) or buy_check_touch_middle(end):
    #     return True
    return False



def sell_check(percent, end):
    if check_special(end) == -1:
        return True
    if sell_check_special(end):
        return True
    # 如果买入条件2与卖出条件1同时出现，先执行买入条件2；
    if buy_check_touch_middle(end) and sell_check_touch_high(percent, end):
        return False
    if sell_check_touch_high(percent, end) or sell_check_touch_middle(end):
        return True
    return False


def sell(stock_code, isCharge, day, price):
    global num
    global cost
    global all
    global principal
    global transaction_signal
    #if sell_check(percent, day) and num > 0:
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


#止损
def stop_loss(stock_code,isCharge, day, price):
    global num
    global cost
    global all
    global principal
    global begin
    global transaction_signal

    transaction_signal.append(-1)
    #if num != 0 and all < begin and abs(all - principal - begin) >= stoploss * (all - principal):
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

# 参数从左到右依次是初始本金，股票代码，RSI-6变化比率，止损比率，回测周期，是否计算手续费
def trading_strategy2_whole(principal, stock_code, percent, stoploss, span, isCharge):
    global history_240
    # 取数起始日期
    start = history_240['trade_date'][len(history_240) - 1]
    start = history_240.loc[history_240['trade_date'] == start].index[0]
    # print(start)
    # 回测日期列表
    a = history_240
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
        # print(history_data,now_data)
        # break
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


# 参数从左到右依次是初始本金，股票代码，RSI-6变化比率，止损比率，回测周期，是否计算手续费
def trading_strategy2_position(principa, stock_code, percent, stoploss, span, isCharge):
    global history_240
    global condition_step
    global num
    global cost
    global all
    global principal
    global begin
    # 取数起始日期
    start = history_240['trade_date'][len(history_240) - 1]
    start = history_240.loc[history_240['trade_date'] == start].index[0]
    # 回测日期列表
    day = history_240['trade_date'][-(span):]
    # 仓位，单位是股数
    num = 0
    # 总资产数
    principal = principa
    all = principal
    # 起始资金数，用于判断是否需要强制止损
    begin = principal
    # db = database_connection.MySQLDb()
    # 用迭代器跳过指定天数
    day_iter = iter(day)
    for d in day_iter:
    # for d in day:
        end = history_240.loc[history_240['trade_date'] == d].index[0]
        global history_data
        history_data = history_240.loc[start:end]
        history_data = history_data.reset_index(drop=True)
        history_data = history_data.iloc[::-1]
        history_data = history_data.reset_index(drop=True)
        history_data = history_data.sort_index(ascending=False)
        date = history_data['trade_date'].values[-1]
        global now_data
        now_data = history_240[history_240['trade_date'] == d]

        # test 条件三
        # print(buy_check_condition_three(date))
        #
        # condition_step = 0

        price = now_data['close'].values[-1]
        # 单笔交易至少有100股
        if principal > price * 100:
            if (buy_check(percent, d)) :
                buy(stock_code, isCharge, d, price)
            elif buy_check_touch_low(percent, d):
                sell_check_condition_three(d)
                if condition_step != 0:
                    break
            #哪个优先级高
            elif buy_check_touch_low(percent,d) or is_buy_condition_three(d):
                if is_buy_condition_three(d):
                    new_d = check_buy_condition_three(stock_code, isCharge, d, price)
                    span_days = workdays(datetime.strptime(d,'%Y%m%d'),datetime.strptime(new_d,'%Y%m%d'))
                    # 跳过指定天数
                    for i in range(span_days):
                        next(day_iter)
                else:
                    buy(stock_code,isCharge,d,price)

        # if (buy_check(percent, date)) & (principal > price * 100):
        #
        #     # 剩余仓位
        #     cost = int(principal / (price * 100))
        #     # 加仓2p-1
        #     cost = ((0.7 + winning_percentage()) * 2 - 1) * cost
        #     # 取满100股
        #     cost = math.floor(cost / 100) * 100
        #     if cost > 0:
        #         num += cost * 100
        #         principal -= cost * price * 100
        #         charge = 0
        #         if isCharge:
        #             charge = cost * price * 100 * 0.0003
        #             # 佣金最低5元
        #             if charge < 5:
        #                 charge = 5
        #             principal -= charge
        #             all -= charge
        #         while principal < 0:
        #             cost -= 1
        #             num -= 100
        #             principal += price * 100
        #     if num > 0:
        #         sql = "INSERT IGNORE INTO backtest2(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
        #                                                     VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
        #               (stock_code, d, True, price, num, charge, False, all)
        #         db.commit_data(sql)
        #         print(d + " " + "buy: " + str(num) + "股 " + "价格：" + str(price) + " 剩余本金： " + str(
        #             principal) + " 总资产： " + str(all) + " 手续费： " + str(charge))

        # 确保有可卖出的股数
        if sell_check(percent, d) and num > 0:
            print('sell')
            sell(stock_code, isCharge, d, price)
        # if sell_check(percent, date) and num > 0:
        #     principal += num * price
        #     all = principal
        #     charge = 0
        #     stamp_tax = 0
        #     if isCharge:
        #         charge = cost * price * 100 * 0.0003
        #         # 佣金最低5元
        #         if charge < 5:
        #             charge = 5
        #         # 印花税
        #         stamp_tax = cost * price * 100 * 0.001
        #         charge += stamp_tax
        #         principal -= charge
        #         all -= charge
        #     sql = "INSERT IGNORE INTO backtest2(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
        #                                                                 VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
        #           (stock_code, d, False, price, num, charge, False, all)
        #     db.commit_data(sql)
        #     print(d + " " + "sell: " + str(num) + "股 " + "价格：" + str(price) + " 剩余本金： " + str(
        #         principal) + " 总资产： " + str(all) + " 佣金： " + str(charge) + " 印花税： " + str(stamp_tax))
        #     num = 0


        # 强制止损
        if num != 0 and all < begin and abs(all - principal - begin) >= stoploss * (all - principal):
            print('stop')
            stop_loss(stock_code, isCharge, d, price)
        # if num != 0 and all < begin and abs(all - principal - begin) >= stoploss * (all - principal):
        #     print("强制止损")
        #     principal += num * price
        #     all = principal
        #     charge = 0
        #     stamp_tax = 0
        #     if isCharge:
        #         charge = cost * price * 100 * 0.0003
        #         # 佣金最低5元
        #         if charge < 5:
        #             charge = 5
        #         # 印花税
        #         stamp_tax = cost * price * 100 * 0.001
        #         charge += stamp_tax
        #         principal -= charge
        #         all -= charge
        #     sql = "INSERT IGNORE INTO backtest2(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
        #                                                                             VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
        #           (stock_code, d, False, price, num, charge, True, all)
        #     db.commit_data(sql)
        #     print(d + " " + "sell: " + str(num) + "股 " + "价格：" + str(price) + " 剩余本金： " + str(
        #         principal) + " 总资产： " + str(all) + " 佣金： " + str(charge) + " 印花税： " + str(stamp_tax))
        #     num = 0
    print("共计： " + str(span) + "个交易日")
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
    start = datetime(int(start_day[0:4]), int(start_day[4:6]), int(start_day[6:8]))
    end = datetime(int(end_day[0:4]), int(end_day[4:6]), int(end_day[6:8]))
    span = workdays(start, end)
    # span = (end - start).days
    day = end
    delta = timedelta(days=240 * 1.5 + 100)  # 采取时间差*1.5+100的方式确保能获得足够的交易日
    n_days_forward = day - delta  # 当前日期向前推n天的时间
    start_day = n_days_forward.strftime('%Y%m%d')
    end_day = day.strftime('%Y%m%d')
    set_info(start_day, end_day, stock_code)
    df = []
    print(start, end, span, day, delta, n_days_forward, start_day, end_day)
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


# 调用示例：
# setdata('20220525', '20220627', '300917.SZ')
# backtest2(30, '300917.SZ', 9999999, 0.1, 0.1, False, True)
# print(buy_check_condition_three('20220627'))
date_backtest2('20220525', '20220627', '300917.SZ', 9999999, 0.1, 0.3, False, False)

# print(getBoll()[1][-1], now_data['high'])
# print(history_240)
# print(getBoll()[1][-1])
# print(now_data['high'])
# midBoll = getBoll()[1][-1]


# high = now_data['high']
# low = now_data['low']
# print((high > midBoll) & (midBoll > low))
