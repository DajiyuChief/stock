import sys
import math

import numpy as np
import pandas as pd
import tushare as ts
from datetime import date, datetime, timedelta
from data_modules import database_connection
from chinese_calendar import is_holiday
import talib as ta

pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')
sys.path.append("../data_modules/database_connection.py")

# 回测前一交易日数据
yesterday_data = pd.DataFrame
# 回测当前交易数据
now_data = pd.DataFrame
# 当前历史数据
history_data = pd.DataFrame
# 至少240日历史数据
history_240 = pd.DataFrame
global_data = pd.DataFrame
transaction_date = pd.DataFrame
sell_signal = []
buy_signal = []
stock_code = ''
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
    get_macd()
    for i in range(len(global_data)):
        transaction_date.append(global_data.trade_date[i])
    transaction_date = sorted(transaction_date)
    # global_data.to_csv('res' + stock + '.csv')
    return global_data


def clear():
    global transaction_date, buy_signal, sell_signal
    buy_signal = []
    sell_signal = []
    transaction_date = []


def setdata(start_day, end_day, stock_code):
    end = datetime(int(end_day[0:4]), int(end_day[4:6]), int(end_day[6:8]))
    day = end
    delta = timedelta(days=240 * 1.5 + 100)  # 采取时间差*1.5+100的方式确保能获得足够的交易日
    n_days_forward = day - delta  # 当前日期向前推n天的时间
    start_day = n_days_forward.strftime('%Y%m%d')
    end_day = day.strftime('%Y%m%d')
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


def get_price(date, type):
    if type == 'close':
        return global_data.loc[global_data['trade_date'] == date].close.values[0]
    elif type == 'open':
        return global_data.loc[global_data['trade_date'] == date].open.values[0]
    elif type == 'high':
        return global_data.loc[global_data['trade_date'] == date].high.values[0]
    elif type == 'low':
        return global_data.loc[global_data['trade_date'] == date].low.values[0]


def get_macd(date):
    return global_data.loc[global_data['trade_date'] == date].macd.values[0]


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


# 基础的买卖条件，分别是日期、类型、macd变化率
def basic_transaction(date, type, percent):
    yesterday = date_calculate(date, -1)
    today_low = get_price(date, 'low')
    yesterday_low = get_price(yesterday, 'low')
    today_high = get_price(date, 'high')
    yesterday_high = get_price(date, 'high')
    today_macd = get_macd(date)
    yesterday_macd = get_macd(yesterday)
    if type == 'buy' and today_low >= yesterday_low and today_macd > (1 + percent) * yesterday_macd:
        return True
    elif type == 'sell' and today_high <= yesterday_high and today_macd < (1 - percent) * yesterday_macd:
        return True
    else:
        return False


# 下面是特殊条件
# 如果当日开盘价高于昨日收盘价，并且当日最高价高于昨日最高价，但为阴线收盘（当日收盘价低于开盘价），且MACD柱值比昨日没有上涨超过10% 以上，看空
def special_1_sell(date, percent):
    yesterday = date_calculate(date, -1)
    today_open = get_price(date, 'open')
    today_close = get_price(date, 'close')
    today_high = get_price(date, 'high')
    yesterday_close = get_price(yesterday, 'close')
    yesterday_high = get_price(yesterday, 'high')
    today_macd = get_macd(date)
    yesterday_macd = get_macd(yesterday)
    if today_open > yesterday_close and today_high > yesterday_high and today_open > today_close and today_macd < (
            1 + percent) * yesterday_macd:
        return True
    else:
        return False


# 当日最低价虽然低于昨日最低价，但是MACD柱值比昨日下降少于30%，且K线为阳线收盘，看多
def special_2_buy(date, percent):
    yesterday = date_calculate(date, -1)
    today_open = get_price(date, 'open')
    today_low = get_price(date, 'low')
    today_close = get_price(date, 'close')
    yesterday_low = get_price(yesterday, 'low')
    today_macd = get_macd(date)
    yesterday_macd = get_macd(yesterday)
    if today_low < yesterday_low and today_close > today_open and today_macd > (1 - percent) * yesterday_macd:
        return True
    else:
        return False


# 当日股价既创新高也创新低，即：最低价比昨日最低价更低，但同时最高价也比昨日最高价更高，此时如K线为阳线收盘且MACD柱值比昨日下降少于30%，看多（有仓位的保持，无仓位的可买入）；否则，看空
def special_3_both(date, percnet):
    yesterday = date_calculate(date, -1)
    today_high = get_price(date, 'high')
    yesterday_high = get_price(yesterday, 'high')
    yesterday = date_calculate(date, -1)
    today_open = get_price(date, 'open')
    today_low = get_price(date, 'low')
    today_close = get_price(date, 'close')
    yesterday_low = get_price(yesterday, 'low')
    today_macd = get_macd(date)
    yesterday_macd = get_macd(yesterday)
    if today_low < yesterday_low and today_high > yesterday_high and today_close > today_open and today_macd > (
            1 - percnet) * yesterday_macd:
        return 'buy'
    else:
        return 'sell'


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


# 不买入的情况, 同时也是优先级最高的卖出条件：
def not_buy_condition():
    # 最近一个“短期最低点”,低于前一个“短期最低点”,且又低于再前一个“短期最低点”
    not_buy = False

    # 最近一个“短期最低点”
    lowest_1 = history_data.loc[0]['low']
    # 是否找到最近一个“短期最低点”
    flag1 = False
    # 最近第二个“短期最低点”
    lowest_2 = history_data.loc[0]['low']
    # 是否找到最近第二个“短期最低点”
    flag2 = False
    # 最近第三个“短期最低点”
    lowest_3 = history_data.loc[0]['low']
    # 是否找到最近第三个“短期最低点”
    flag3 = False

    for i in range(2, len(history_data)):
        left = history_data.loc[i - 2]['low']
        now_lowest = history_data.loc[i - 1]['low']
        right = history_data.loc[i]['low']
        # 最低价低于相邻K线的最低价
        if now_lowest < left and now_lowest < right:
            if not flag1:
                lowest_1 = now_lowest
                flag1 = True
                continue
            if not flag2:
                lowest_2 = now_lowest
                flag2 = True
                continue
            if not flag3:
                lowest_3 = now_lowest
                flag3 = True
                break
    # 确保已经有足够进行判断的条件
    if flag1 and flag2 and flag3:
        if lowest_1 < lowest_2 < lowest_3:
            not_buy = True
    return not_buy


# 判断一般情况（对应文档一般情况），返回true/false
def buy_check_normal(percent):
    # 当日最低价大于或等于昨日最低价
    buy_flag1 = False
    # 当日MACD柱值大于昨日MACD柱值指定比例以上
    buy_flag2 = False

    now_low = now_data['low'].values[0]
    # 前一个交易日
    yesterday_low = history_data.loc[1]['low']
    # 当日最低价大于或等于昨日最低价
    if now_low >= yesterday_low:
        buy_flag1 = True

    macd = get_macd()
    now_macd = macd[0]
    yesterday_macd = macd[1]
    # 当日MACD柱值大于昨日MACD柱值10%以上
    if now_macd - yesterday_macd > 0 and (now_macd - yesterday_macd) > abs(yesterday_macd) * percent:
        buy_flag2 = True

    # 同时满足
    return buy_flag1 & buy_flag2


# 判断特殊情况（对应文档例外情况（2），满足该情况会强制执行），返回true/false
def buy_check_special():
    # 当日收盘价高于开盘价
    positive = False
    # macd柱值比昨日下降少于30%
    macd_check = False

    now_open = now_data['open'].values[0]
    now_close = now_data['close'].values[0]
    # 阳线收盘，当日收盘价高于开盘价
    if now_close > now_open:
        positive = True

    macd = get_macd()
    now_macd = macd[0]
    yesterday_macd = macd[1]
    # macd柱值比昨日下降少于30%
    if yesterday_macd - now_macd > 0 and (yesterday_macd - now_macd) <= abs(yesterday_macd) * 0.3:
        macd_check = True

    # 同时满足
    return positive & macd_check


# 判断特殊情况（对应文档例外情况（5）三日内的最高价已超过最近的最高价，同时该日 MACD 柱值 大于前一日 MACD 柱值 30%以上
def buy_check_high():
    # 三日内的最高价已超过离卖出时最近的最高价
    buy_flag1 = False
    # 该日 MACD 柱值 大于前一日 MACD 柱值 30%以上
    buy_flag2 = False

    highest = max(history_data.loc[0]['high'], history_data.loc[1]['high'], history_data.loc[2]['high'])
    # 最近一个“短期最高点”
    highest_1 = history_data.loc[0]['high']
    # 是否找到最近一个“短期最高点”
    flag1 = False

    for i in range(2, len(history_data)):
        left = history_data.loc[i - 2]['high']
        now = history_data.loc[i - 1]['high']
        right = history_data.loc[i]['high']
        # 最高价高于相邻K线的最高价
        if now > left and now > right:
            if not flag1:
                highest_1 = now
                flag1 = True
                break
    if flag1:
        if highest > highest_1:
            buy_flag1 = True

    macd = get_macd()
    now_macd = macd[0]
    yesterday_macd = macd[1]
    # 当日MACD柱值大于昨日MACD柱值30%以上
    if now_macd - yesterday_macd > 0 and (now_macd - yesterday_macd) > abs(yesterday_macd) * 0.3:
        buy_flag2 = True

    return buy_flag1 & buy_flag2


# 判断特殊情况（对应文档例外情况（3），满足该情况会强制执行），返回-1，0，1，1表示买入，-1表示卖出，0表示不交易
def check_special():
    # 当日最高价高于昨日最高价
    higher = False
    # 当日最低价低于昨日最低价
    lower = False
    # 阳线收盘 & macd柱值比昨日下降少于30%
    candle_check = buy_check_special()

    now_high = now_data['high'].values[0]
    # 前一个交易日
    yesterday_high = history_data.loc[1]['high']
    # 当日最高价高于昨日最高价
    if now_high > yesterday_high:
        higher = True

    now_low = now_data['low'].values[0]
    # 前一个交易日
    yesterday_low = history_data.loc[1]['low']
    # 当日最低价低于昨日最低价
    if now_low < yesterday_low:
        lower = True

    # 同时新高新低
    if higher and lower:
        if candle_check:
            return 1
        else:
            return -1

    return 0


# 判断一般情况（对应文档一般情况），返回true/false
def sell_check_normal(percent):
    # 当日最高价小于或等于昨日最高价
    sell_flag1 = False
    # 当日MACD柱值小于昨日MACD柱值指定比例以上
    sell_flag2 = False

    now_high = now_data['high'].values[0]
    # 前一个交易日
    yesterday_high = history_data.loc[1]['high']
    # 当日最高价小于或等于昨日最高价
    if now_high <= yesterday_high:
        sell_flag1 = True

    macd = get_macd()
    now_macd = macd[0]
    yesterday_macd = macd[1]
    # 当日MACD柱值小于昨日MACD柱值指定比例以上
    if now_macd - yesterday_macd < 0 and (yesterday_macd - now_macd) < abs(yesterday_macd) * percent:
        sell_flag2 = True

    # 同时满足
    return sell_flag1 & sell_flag2


# 判断特殊情况（对应文档例外情况（1），满足该情况会强制执行），返回true/false
def sell_check_special():
    # 当日收盘价低于开盘价
    negative = False
    # macd柱值比昨日没有上涨超过10%以上
    macd_check = False

    now_open = now_data['open'].values[0]
    now_close = now_data['close'].values[0]
    # 阴线收盘，当日收盘价低于开盘价
    if now_close < now_open:
        negative = True

    macd = get_macd()
    now_macd = macd[0]
    yesterday_macd = macd[1]
    # macd柱值比昨日没有上涨超过10%以上
    if now_macd - yesterday_macd > 0 and (now_macd - yesterday_macd) <= abs(yesterday_macd) * 0.1:
        macd_check = True

    # 同时满足
    return negative & macd_check


# 判断特殊情况（对应文档例外情况（4）三日内的最低价已低于最近的最低价，同时该日 MACD 柱值小于前一日的 MACD 柱值 30%以上。
def sell_check_low():
    # 三日内的最低价已超过最近的最低价
    sell_flag1 = False
    # 同时该日 MACD 柱值小于前一日的 MACD 柱值 30%以上。
    sell_flag2 = False

    lowest = max(history_data.loc[0]['low'], history_data.loc[1]['low'], history_data.loc[2]['low'])
    # 最近一个“短期最低点”
    lowest_1 = history_data.loc[0]['low']
    # 是否找到最近一个“短期最低点”
    flag1 = False

    for i in range(2, len(history_data)):
        left = history_data.loc[i - 2]['low']
        now = history_data.loc[i - 1]['low']
        right = history_data.loc[i]['low']
        # 最低价低于相邻K线的最低价
        if now < left and now < right:
            if not flag1:
                lowest_1 = now
                flag1 = True
                break
    if flag1:
        if lowest < lowest_1:
            sell_flag1 = True

    macd = get_macd()
    now_macd = macd[0]
    yesterday_macd = macd[1]
    # 该日 MACD 柱值小于前一日的 MACD 柱值 30%以上
    if now_macd - yesterday_macd < 0 and abs(now_macd - yesterday_macd) > abs(yesterday_macd) * 0.3:
        sell_flag2 = True

    return sell_flag1 & sell_flag2


# 前三个交易日是否有买入记录，True为有，False为没有
def check_buy_3day():
    df = []
    data = history_data
    date1 = data.loc[1]["trade_date"]
    date2 = data.loc[2]["trade_date"]
    date3 = data.loc[3]["trade_date"]
    stock_code = history_data.loc[0]['ts_code']
    db = database_connection.MySQLDb()
    sql = "SELECT * FROM backtest1 WHERE date=%s AND code='%s' AND type=TRUE " % (date1, stock_code)
    df.append(db.select_one(sql))
    sql = "SELECT * FROM backtest1 WHERE date=%s AND code='%s' AND type=TRUE " % (date2, stock_code)
    df.append(db.select_one(sql))
    sql = "SELECT * FROM backtest1 WHERE date=%s AND code='%s' AND type=TRUE " % (date3, stock_code)
    df.append(db.select_one(sql))
    if len(df) == 0:
        return False
    return True


# 前三个交易日是否有卖出记录，True为有，False为没有
def check_sell_3day():
    df = []
    data = history_data
    date1 = data.loc[1]["trade_date"]
    date2 = data.loc[2]["trade_date"]
    date3 = data.loc[3]["trade_date"]
    stock_code = history_data.loc[0]['ts_code']
    db = database_connection.MySQLDb()
    sql = "SELECT * FROM backtest1 WHERE date=%s AND code='%s' AND type=FALSE " % (date1, stock_code)
    df.append(db.select_one(sql))
    sql = "SELECT * FROM backtest1 WHERE date=%s AND code='%s' AND type=FALSE " % (date2, stock_code)
    df.append(db.select_one(sql))
    sql = "SELECT * FROM backtest1 WHERE date=%s AND code='%s' AND type=FALSE " % (date3, stock_code)
    df.append(db.select_one(sql))
    if len(df) == 0:
        return False
    return True


# 按照文档的计算方式
# def get_macd():
#     global global_data
#     df = global_data
#     # 12日均值
#     shortEMA = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()
#     # 26日均值
#     longEMA = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()
#     # 差值
#     DIFF = shortEMA - longEMA
#     DEA = DIFF.ewm(span=9, adjust=False, min_periods=9).mean()
#     MACD = DIFF - DEA
#     MACD *= 2
#     global_data['macd'] = MACD
#     return MACD


def buy_check(percent):
    if not_buy_condition():
        return False
    if check_special() == 1:
        return True
    if buy_check_special():
        return True
    if buy_check_high():
        return True
    if buy_check_normal(percent) and not check_sell_3day():
        return True
    return False


def sell_check(percent):
    if not_buy_condition():
        return True
    if check_special() == -1:
        return True
    if sell_check_special():
        return True
    if sell_check_low():
        return True
    if sell_check_normal(percent) and not check_buy_3day():
        return True
    return False


# 参数从左到右依次是初始本金，股票代码，MACD柱值变化检测比率，止损比率，回测周期，是否计算手续费
def trading_strategy1_whole(principal, stock_code, percent, stoploss, span, isCharge):
    global history_240
    # 取数起始日期
    start = history_240['trade_date'][len(history_240) - 1]
    start = history_240.loc[history_240['trade_date'] == start].index[0]
    # 回测日期列表
    day = history_240['trade_date'][-(span):]
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
                sql = "INSERT IGNORE INTO backtest1(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
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
            sql = "INSERT IGNORE INTO backtest1(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
                                                                    VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
                  (stock_code, d, False, price, 0, charge, False, all)
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
            sql = "INSERT IGNORE INTO backtest1(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
                                                                                VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
                  (stock_code, d, False, price, 0, charge, False, all)
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


# 参数从左到右依次是初始本金，股票代码，MACD柱值变化检测比率，止损比率，回测周期，是否计算手续费
def trading_strategy1_position(principal, stock_code, percent, stoploss, span, isCharge):
    global history_240
    # 取数起始日期
    start = history_240['trade_date'][len(history_240) - 1]
    start = history_240.loc[history_240['trade_date'] == start].index[0]
    # 回测日期列表
    day = history_240['trade_date'][-(span):]
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
            # 剩余仓位
            cost = int(principal / (price * 100))
            # 加仓2p-1
            cost = ((0.7 + winning_percentage()) * 2 - 1) * cost
            # 取满100股
            cost = math.floor(cost / 100) * 100
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
                sql = "INSERT IGNORE INTO backtest1(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
                                                            VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
                      (stock_code, d, True, price, num, charge, False, all)
                db.commit_data(sql)
                print(d + " " + "buy: " + str(num) + "股 " + "价格：" + str(price) + " 剩余本金： " + str(
                    principal) + " 总资产： " + str(all) + " 手续费： " + str(charge))
        # 确保有可卖出的股数
        if sell_check(percent) and num > 0:
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
            sql = "INSERT IGNORE INTO backtest1(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
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
            sql = "INSERT IGNORE INTO backtest1(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
                                                                                    VALUES ('%s', '%s',  %d,  %f,  %f, %f, %d, %f)" % \
                  (stock_code, d, False, price, num, charge, True, all)
            db.commit_data(sql)
            print(d + " " + "sell: " + str(num) + "股 " + "价格：" + str(price) + " 剩余本金： " + str(
                principal) + " 总资产： " + str(all) + " 佣金： " + str(charge) + " 印花税： " + str(stamp_tax))
            num = 0
    print("共计： " + str(span) + "个交易日")
    return all


def backtest1(span, stock_code, principal, percent, stoploss, isCharge, isWhole):
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
    db.clean_table("TRUNCATE TABLE `backtest1`;")
    if isWhole:
        return trading_strategy1_whole(principal, stock_code, percent, stoploss, span, isCharge)
    else:
        return trading_strategy1_position(principal, stock_code, percent, stoploss, span, isCharge)


def date_backtest1(start_day, end_day, stock_code, principal, percent, stoploss, isCharge, isWhole):
    start = datetime(int(start_day[0:4]), int(start_day[4:6]), int(start_day[6:8]))
    end = datetime(int(end_day[0:4]), int(end_day[4:6]), int(end_day[6:8]))
    span = (end - start).days
    day = end
    delta = timedelta(days=240 * 1.5 + 100)  # 采取时间差*1.5+100的方式确保能获得足够的交易日
    n_days_forward = day - delta  # 当前日期向前推n天的时间
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
    db.clean_table("TRUNCATE TABLE `backtest1`;")
    if isWhole:
        return trading_strategy1_whole(principal, stock_code, percent, stoploss, span, isCharge)
    else:
        return trading_strategy1_position(principal, stock_code, percent, stoploss, span, isCharge)


# 调用示例：
# backtest1(30, '600795.SH', 9999999, 0.3, 0.1, False, False)
set_info('20220101', '20220303', '600795.SH')
print(global_data)
# date_backtest1('20220101', '20220303', '600795.SH', 9999999, 0.3, 0.1, False, False)

# load_historical_data('600795.SH', '20220101', '20220303')
# print(history_data)
