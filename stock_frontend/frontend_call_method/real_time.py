import os
import sys

import easyquotation
import pandas as pd

o_path = os.getcwd()
sys.path.append(o_path)
sys.path.append("../../stock_trading_strategy/trading_strategy_1/trading.py.py")
from trading_strategy_1 import trading
sys.path.append("../../stock_trading_strategy/trading_strategy_2/trading2.py.py")
from trading_strategy_2 import trading2
# 显示所有行
pd.set_option('display.max_rows', 100000)
# 设置数据接口
quotation = easyquotation.use('sina')  # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
# quotation = easyquotation.use('tencent')


def get_real_time_data(stock_code):
    stock_code = stock_code_convert(stock_code)
    data = quotation.real(stock_code)
    lst = []
    lst.append(data[stock_code[2:]]['name'])
    lst.append(data[stock_code[2:]]['now'])
    lst.append(data[stock_code[2:]]['open'])
    lst.append(data[stock_code[2:]]['high'])
    lst.append(data[stock_code[2:]]['low'])
    lst.append(data[stock_code[2:]]['turnover'])
    # print(data[stock_code[2:]])
    # print(data[stock_code[2:]]['now'])
    return lst


def stock_code_convert(stock_code):
    lst = stock_code.split('.')
    type = lst[1].lower()
    return type + lst[0]


def suggest1(stock_code, percent):
    return trading.real_time_trading(stock_code, percent)

def suggest2(stock_code, percent):
    return trading2.real_time_trading(stock_code, percent)

