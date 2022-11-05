from datetime import date, datetime, timedelta
import sys
import easyquotation
import pandas as pd
import tushare as ts
import talib as ta
pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')
sys.path.append("../data_modules/database_connection.py")
from data_modules import database_connection
# 设置数据接口
quotation = easyquotation.use('sina')  # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
# quotation = easyquotation.use('tencent')

# 当前交易数据
now_data = pd.DataFrame
# 历史数据
history_data = pd.DataFrame

# 显示所有行
pd.set_option('display.max_rows', 1000)
# 显示所有列
pd.set_option('display.max_columns', 1000)


def load_data(stock_code, start_day, end_day):
    df = []
    while True:
        try:
            df = pro.daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
            break
        except:
            continue
    df = df.sort_values(by='trade_date', ascending=True)
    global history_data
    history_data = df
    code = stock_code_convert(stock_code)
    data = []
    while True:
        try:
            data = quotation.real(code)
            break
        except:
            continue
    global now_data
    now_data = data[stock_code[:-3]]
    return


# 股票代码格式转换
def stock_code_convert(stock_code):
    lst = stock_code.split('.')
    type = lst[1].lower()
    return type + lst[0]


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
    low = now_data['low']
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
    high = now_data['high']
    #改1
    low = now_data['low']
    if high > midBoll > low:
        flag1 = True
    if flag1:
        open = now_data['open']
        close = now_data['close']
        if close > open:
            flag2 = True
    return flag2


# 对应文档特殊情况1
def buy_check_special():
    # 触及上沿线
    flag1 = False

    flag2 = False

    high = now_data['high']
    highBoll = getBoll()[0][-1]
    if high >= highBoll:
        flag1 = True
    if flag1:
        # 回溯前30天
        history_30 = history_data[-30:]
        for i in range(0, 30):
            close = history_data[-30:].loc[i]['close']
            # 下降达到中界线
            if close <= getBoll()[1][-(1+i)]:
                break
            high = history_data[-30:].loc[i]['high']
            # 股价上一次触及上沿线
            if high >= getBoll()[0][-(1+i)]:
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
    high = now_data['high']
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
    low = now_data['low']
    #gai2
    high = now_data['high']
    if low < midBoll < high:
        flag1 = True
    if flag1:
        open = now_data['open']
        close = now_data['close']
        if close < open:
            flag2 = True
    return flag2


# 对应文档特殊情况2
def sell_check_special():
    # 触及下沿线
    flag1 = False

    flag2 = False

    low = now_data['low']
    lowBoll = getBoll()[2][-1]
    if low <= lowBoll:
        flag1 = True
    if flag1:
        # 回溯前30天
        for i in range(0, 30):
            close = history_data[-30:].loc[i]['close']
            # 上升达到中界线
            if close >= getBoll()[1][-(1+i)]:
                break
            low = history_data[-30:].loc[i]['low']
            # 股价上一次触及下沿线
            if low <= getBoll()[2][-(1+i)]:
                if i > 3:
                    flag2 = True
                break

    return flag2

# 特殊情况3
def check_special():
    highBoll = getBoll()[0][-1]
    high = now_data['high']
    lowBoll = getBoll()[2][-1]
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


# 参数从左到右依次是股票代码，RSI-6变化比率
def trading(stock_code, percent):
    price = now_data['close']
    day = now_data['date']
    time = now_data['time']
    buy = False
    sell = False
    db = database_connection.MySQLDb()
    if buy_check(percent):
        sql = "INSERT IGNORE INTO actual2(code, date, time, type, price) \
               VALUES ('%s', '%s',  '%s',  %d,  %f);" % \
              (stock_code, day, time, True, price)
        db.commit_data(sql)
        print(day + " " + time + " " + "建议买入" + "  " + "价格：" + str(price))
        buy = True
    if sell_check(percent):
        sql = "INSERT IGNORE INTO actual2(code, date, time, type, price) \
                       VALUES ('%s', '%s',  '%s',  %d,  %f);" % \
              (stock_code, day, time, False, price)
        db.commit_data(sql)
        print(day + " " + time + " " + "建议卖出" + "  " + "价格：" + str(price))
        sell = True
    return buy, sell


def real_time_trading(stock_code, percent):
    day = date.today()  # 当前日期
    now = datetime.now()
    delta = timedelta(days=240 * 1.5 + 100)  # 采取时间差*1.5+100的方式确保能获得足够的交易日
    n_days_forward = now - delta  # 当前日期向前推n天的时间
    start_day = n_days_forward.strftime('%Y%m%d')
    end_day = day.strftime('%Y%m%d')
    load_data(stock_code, start_day, end_day)
    db = database_connection.MySQLDb()
    try:
        db.clean_table("TRUNCATE TABLE `actual2`;")
    except Exception as e:
        print(e)
    return trading(stock_code, percent)

# 调用示例
# print(real_time_trading('600795.SH', 0.1))
print(real_time_trading('600795.SH', 0.2))