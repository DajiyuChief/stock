from datetime import datetime

from trading2 import getBoll

from backtest2 import setdata
from backtest2 import getRSI
import talib as ta
import tushare as ts
from backtest2 import workdays
from chinese_calendar import is_workday
from datetime import datetime, timedelta
from chinese_calendar import is_holiday
pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')

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
    return high,middle,low


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



data = setdata('20220320', '20220615', '600256.SH')
data2 = setdata('20220320', '20220627', '300917.SZ')
close = data.close.values
data['rsi'] = ta.RSI(close, timeperiod=6)
newget(data)
df = pro.trade_cal(exchange='SZSE', start_date='20220220', end_date='20220627')
da1 = df.loc[df['cal_date' ]== '20220320'].index[0]
da2 = df.loc[df['cal_date' ]== '20220615'].index[0] + 1
# print(data)
# print(data2)

print(workdays(datetime.strptime('20220301', '%Y%m%d'), datetime.strptime('20220331', '%Y%m%d')))
print(tradedays(datetime.strptime('20220301', '%Y%m%d'), datetime.strptime('20220331', '%Y%m%d')))
