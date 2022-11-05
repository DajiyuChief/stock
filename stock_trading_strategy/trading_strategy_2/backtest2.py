import math
import sys
import pandas as pd
import pymysql
import tushare as ts
import talib as ta
from datetime import date, datetime, timedelta

pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')
sys.path.append("../data_modules/database_connection.py")
from data_modules import database_connection

# 回测前一交易日数据
yesterday_data = pd.DataFrame
# 回测当前交易数据
now_data = pd.DataFrame
# 当前历史数据
history_data = pd.DataFrame
# 至少240日历史数据
history_240 = pd.DataFrame

# 显示所有行
pd.set_option('display.max_rows', 1000)
# 显示所有列
pd.set_option('display.max_columns', 1000)



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

    global history_240
    history_240 = df
    global history_data
    history_data = df

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


def getBoll():
    global history_data
    df = history_data
    high, middle, low = ta.BBANDS(
        df['close'].values,
        timeperiod=20,
        # 与平均值的无偏倚标准差的数量
        nbdevup=2,
        nbdevdn=2,
        # 移动平均线类型：0为简单移动平均线
        matype=0)
    # high: getBoll()[0]
    return high, middle, low


def getRSI():
    global history_data
    df = history_data
    # 6日rsi
    rsi = ta.RSI(df['close'].values, timeperiod=6)
    return rsi


# 买入条件：触及下沿线情况
# percent为用户指定的比例
def buy_check_touch_low(percent):
    # 股票最低价已经触及布林线下沿线
    flag1 = False
    # 在（1）成立的前提下，出现RSI-6 大于上一日指定比例时买入
    flag2 = False

    lowBoll = getBoll()[2][-1]
    low = now_data['low'].values[0]
    if lowBoll >= low:
        flag1 = True
    if flag1:
        nowRSI = getRSI()[-1]
        yesterdayRSI = getRSI()[-2]
        if nowRSI > (yesterdayRSI * (1 + percent)):
            flag2 = True
    return flag2


# 买入条件：触及中界线情况
def buy_check_touch_middle():
    # 股价从下往上越过中界线，即最高价大于中界线
    flag1 = False
    # 收盘为阳线，即收盘价高于开盘价
    flag2 = False

    midBoll = getBoll()[1][-1]
    high = now_data['high'].values[0]
    # 改1
    low = now_data['low'].values[0]
    if (high > midBoll) & (midBoll > low):
        flag1 = True
    if flag1:
        open = now_data['open'].values[0]
        close = now_data['close'].values[0]
        if close > open:
            flag2 = True
    return flag2


# 对应文档特殊情况1
def buy_check_special():
    # 触及上沿线
    flag1 = False

    flag2 = False

    high = now_data['high'].values[0]
    highBoll = getBoll()[0][-1]
    if high >= highBoll:
        flag1 = True
    if flag1:
        # 回溯前30天
        # history_30 = history_data[-30:]
        for i in range(0, 30):
            close = history_data[-30:].loc[i]['close']
            # 下降达到中界线
            if close <= getBoll()[1][-(1 + i)]:
                break
            high = history_data[-30:].loc[i]['high']
            # 股价上一次触及上沿线
            if high >= getBoll()[0][-(1 + i)]:
                if i > 3:
                    flag2 = True
                break

    return flag2


# RSI-6 下降到 20 以下
def buy_check_rsi():
    nowRSI = getRSI()[-1]
    if nowRSI < 20:
        return True
    return False


# 卖出条件：触及上沿线情况
# percent为用户指定的比例
def sell_check_touch_high(percent):
    # 股票最高价已经触及布林线上沿线
    flag1 = False
    # 在（1）成立的前提下，在出现RSI-6 小于上一日指定比例时卖出
    flag2 = False

    highBoll = getBoll()[0][-1]
    high = now_data['high'].values[0]
    if high >= highBoll:
        flag1 = True
    if flag1:
        nowRSI = getRSI()[-1]
        yesterdayRSI = getRSI()[-2]
        if nowRSI < (yesterdayRSI * (1 - percent)):
            flag2 = True
    return flag2


# 卖出条件：触及中界线情况
def sell_check_touch_middle():
    # 股价从上往下越过中界线，即最低价小于中界线
    flag1 = False
    # 收盘为阴线，即收盘价低于开盘价
    flag2 = False

    midBoll = getBoll()[1][-1]
    low = now_data['low'].values[0]
    # gai2
    high = now_data['high'].values[0]
    if low < midBoll < high:
        flag1 = True
    if flag1:
        open = now_data['open'].values[0]
        close = now_data['close'].values[0]
        if close < open:
            flag2 = True
    return flag2


# 对应文档特殊情况2
def sell_check_special():
    # 触及下沿线
    flag1 = False

    flag2 = False

    low = now_data['low'].values[0]
    lowBoll = getBoll()[2][-1]
    if low <= lowBoll:
        flag1 = True
    if flag1:
        # 回溯前30天
        for i in range(0, 30):
            close = history_data[-30:].loc[i]['close']
            # 上升达到中界线
            if close >= getBoll()[1][-(1 + i)]:
                break
            low = history_data[-30:].loc[i]['low']
            # 股价上一次触及下沿线
            if low <= getBoll()[2][-(1 + i)]:
                if i > 3:
                    flag2 = True
                break

    return flag2


# 特殊情况3
def check_special():
    highBoll = getBoll()[0][-1]
    high = now_data['high'].values[0]
    lowBoll = getBoll()[2][-1]
    low = now_data['low'].values[0]
    if high >= highBoll and lowBoll >= low:
        open = now_data['open'].values[0]
        close = now_data['close'].values[0]
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


def buy_check(percent):
    if check_special() == 1:
        return True
    if buy_check_special():
        return True
    # 如果买入条件1与卖出条件2同时出现，先执行卖出条件2；
    if buy_check_touch_low(percent) and sell_check_touch_middle():
        return False
    if buy_check_touch_low(percent) or buy_check_touch_middle():
        return True
    return False


def sell_check(percent):
    if check_special() == -1:
        return True
    if sell_check_special():
        return True
    # 如果买入条件2与卖出条件1同时出现，先执行买入条件2；
    if buy_check_touch_middle() and sell_check_touch_high(percent):
        return False
    if sell_check_touch_high(percent) or sell_check_touch_middle():
        return True
    return False


# 参数从左到右依次是初始本金，股票代码，RSI-6变化比率，止损比率，回测周期，是否计算手续费
def trading_strategy2_whole(principal, stock_code, percent, stoploss, span, isCharge):
    global history_240
    # 取数起始日期
    start = history_240['trade_date'][len(history_240) - 1]
    start = history_240.loc[history_240['trade_date'] == start].index[0]
    print(start)
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
def trading_strategy2_position(principal, stock_code, percent, stoploss, span, isCharge):
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
                sql = "INSERT IGNORE INTO backtest2(CODE, DATE, TYPE, PRICE, NUM, poundage, stoploss, total) \
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
                  (stock_code, d, False, price, num, charge, True, all)
            db.commit_data(sql)
            print(d + " " + "sell: " + str(num) + "股 " + "价格：" + str(price) + " 剩余本金： " + str(
                principal) + " 总资产： " + str(all) + " 佣金： " + str(charge) + " 印花税： " + str(stamp_tax))
            num = 0
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
    span = (end - start).days
    day = end
    delta = timedelta(days=240 * 1.5 + 100)  # 采取时间差*1.5+100的方式确保能获得足够的交易日
    n_days_forward = day - delta  # 当前日期向前推n天的时间
    start_day = n_days_forward.strftime('%Y%m%d')
    end_day = day.strftime('%Y%m%d')
    df = []
    print(start,end,span,day,delta,n_days_forward,start_day,end_day)
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
#setdata('20220525', '20220627', '300917.SZ')
#backtest2(30, '300917.SZ', 9999999, 0.1, 0.1, False, True)
date_backtest2('20220525', '20220627', '300917.SZ', 9999999, 0.1, 0.3, False, False)

#print(getBoll()[1][-1], now_data['high'])
# print(history_240)
# print(getBoll()[1][-1])
# print(now_data['high'])
# midBoll = getBoll()[1][-1]
# high = now_data['high']
# low = now_data['low']
# print((high > midBoll) & (midBoll > low))