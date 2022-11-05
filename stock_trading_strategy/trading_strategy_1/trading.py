from datetime import date, datetime, timedelta
import sys
import easyquotation
import pandas as pd
import tushare as ts

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

    now_low = now_data['low']
    # 前一个交易日
    yesterday_low = history_data.loc[0]['low']
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

    now_open = now_data['open']
    now_close = now_data['close']
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

    now_high = now_data['high']
    # 前一个交易日
    yesterday_high = history_data.loc[1]['high']
    # 当日最高价高于昨日最高价
    if now_high > yesterday_high:
        higher = True

    now_low = now_data['low']
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

    now_high = now_data['high']
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

    now_open = now_data['open']
    now_close = now_data['close']
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


# 按照文档的计算方式
def get_macd():
    df = history_data[['trade_date', 'close']]
    now_price = now_data['now']
    now_date = now_data['date'].replace('-', '')
    add = {'trade_date': now_date, 'close': now_price}
    df = df.copy()
    df.loc[len(df)] = add
    # 12日均值
    shortEMA = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()
    # 26日均值
    longEMA = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()
    # 差值
    DIFF = shortEMA - longEMA
    DEA = DIFF.ewm(span=9, adjust=False, min_periods=9).mean()
    MACD = DIFF - DEA
    MACD *= 2
    return MACD


def buy_check(percent):
    if not_buy_condition():
        return False
    if check_special() == 1:
        return True
    if buy_check_special():
        return True
    if buy_check_high():
        return True
    if buy_check_normal(percent):
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
    if sell_check_normal(percent):
        return True
    return False


# 参数从左到右依次是股票代码，MACD柱值变化检测比率
def trading(stock_code, percent):
    price = now_data['close']
    day = now_data['date']
    time = now_data['time']
    buy = False
    sell = False
    db = database_connection.MySQLDb()
    if buy_check(percent):
        sql = "INSERT IGNORE INTO actual1(code, date, time, type, price) \
               VALUES ('%s', '%s',  '%s',  %d,  %f);" % \
              (stock_code, day, time, True, price)
        db.commit_data(sql)
        print(day + " " + time + " " + "建议买入" + "  " + "价格：" + str(price))
        buy = True
    if sell_check(percent):
        sql = "INSERT IGNORE INTO actual1(code, date, time, type, price) \
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
        db.clean_table("TRUNCATE TABLE `actual1`;")
    except Exception as e:
        print(e)
    return trading(stock_code, percent)

# 调用示例
# print(real_time_trading('600795.SH', 0.1))
