import tushare as ts
import easyquotation
from datetime import date, datetime, timedelta
pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')
# 设置数据接口
quotation = easyquotation.use('sina')  # 新浪 ['sina'] 腾讯 ['tencent', 'qq']

# 股票代码格式转换
def stock_code_convert(stock_code):
    lst = stock_code.split('.')
    type = lst[1].lower()
    return type + lst[0]

# 获取股票名称
def getName(stock_code):
    code = stock_code_convert(stock_code)
    data = quotation.real(code)[stock_code[:-3]]['name']
    return data

# 回测调用
# 获取指定日期的macd柱值，当所给日期不是交易日时会返回最近一个交易日的macd数值
def get_oneday_macd(stock_code, end_day):
    delta = timedelta(days=34 * 1.5 + 50)
    d1 = datetime(int(end_day[0:4]), int(end_day[4:6]), int(end_day[6:]))
    n_days_forward = d1 - delta
    start_day = n_days_forward.strftime('%Y%m%d')
    df = pro.daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
    df = df.sort_values(by='trade_date', ascending=True)
    # 12日均值
    shortEMA = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()
    # 26日均值
    longEMA = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()
    # 差值
    DIFF = shortEMA - longEMA
    DEA = DIFF.ewm(span=9, adjust=False, min_periods=9).mean()
    MACD = DIFF - DEA
    MACD *= 2
    return MACD.loc[0]


# 实时交易调用
# 非交易时调用会导致最后一个交易日被计算两次
def get_rightnow_macd(stock_code):
    day = date.today()  # 当前日期
    now = datetime.now()
    delta = timedelta(days=240 * 1.5 + 100)  # 采取时间差*1.5+100的方式确保能获得足够的交易日
    n_days_forward = now - delta  # 当前日期向前推n天的时间
    start_day = n_days_forward.strftime('%Y%m%d')
    end_day = day.strftime('%Y%m%d')
    df = pro.daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
    df = df.sort_values(by='trade_date', ascending=True)
    df = df[['trade_date', 'close']]
    df.reset_index(drop=True, inplace=True)

    code = stock_code_convert(stock_code)
    data = quotation.real(code)
    global now_data
    now_data = data[stock_code[:-3]]
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
    return MACD.loc[len(MACD)-1]


# 股票代码格式转换
def stock_code_convert(stock_code):
    lst = stock_code.split('.')
    type = lst[1].lower()
    return type + lst[0]

# 调用示例
# get_oneday_macd('600795.SH', '20210531')
# get_rightnow_macd('600795.SH')

# 示例
# 获取股票名称
# print(getName('600795.SH'))