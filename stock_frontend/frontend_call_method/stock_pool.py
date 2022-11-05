import os

import pandas as pd

from stock_frontend.frontend_call_method.real_time import get_real_time_data

o_path = os.getcwd()
current_path = os.path.dirname(__file__)
from pyarrow import feather


def save_static_strategy1():
    df = static_strategy1()
    feather.write_feather(df, './' + 'strayegy1' + '.feather')
    return


def save_static_strategy2():
    df = static_strategy2()
    feather.write_feather(df, './' + 'strayegy2' + '.feather')
    return


def static_strategy1():
    data = list(pd.read_csv(current_path + '/strategy1.csv', encoding='gbk'))[0:20]
    df = pd.DataFrame(data, columns=['stock'])
    return df


def static_strategy2():
    data = list(pd.read_csv(current_path + './strategy2.csv', encoding='gbk'))[0:20]
    df = pd.DataFrame(data, columns=['stock'])
    return df


def static_user():
    data = ['600199.SH', '600200.SH', '600202.SH', '600206.SH', '600207.SH', '600211.SH', '600212.SH', '600215.SH',
            '600216.SH', '600218.SH', '600219.SH', '600220.SH', '600223.SH', '600231.SH', '600232.SH', '600234.SH',
            '600235.SH', '600239.SH', '600241.SH', '600248.SH', '600251.SH', '600256.SH', '600257.SH', '600260.SH',
            '600262.SH', '600266.SH', '600267.SH', '600268.SH', '600272.SH', '600273.SH', '600277.SH']
    df = pd.DataFrame(data, columns=['stock'])
    return df


def static_strategy1_info():
    df = static_strategy1()['stock']
    items = []
    for stockcode in df:
        get = get_real_time_data(stockcode)
        lst = []
        lst.append(get[0])
        lst.append(stockcode)
        lst.append(get[1])
        lst.append(get[2])
        lst.append(get[3])
        lst.append(get[4])
        lst.append(get[5])
        items.append(lst)
    return items


def static_strategy2_info():
    df = static_strategy2()['stock']
    items = []
    for stockcode in df:
        get = get_real_time_data(stockcode)
        lst = []
        lst.append(get[0])
        lst.append(stockcode)
        lst.append(get[1])
        lst.append(get[2])
        lst.append(get[3])
        lst.append(get[4])
        lst.append(get[5])
        items.append(lst)
    return items


def static_user_stock_info():
    df = static_user()['stock']
    items = []
    for stockcode in df:
        get = get_real_time_data(stockcode)
        lst = []
        lst.append(get[0])
        lst.append(stockcode)
        lst.append(get[1])
        lst.append(get[2])
        lst.append(get[3])
        lst.append(get[4])
        lst.append(get[5])
        items.append(lst)
    return items
# save_static_strategy1()
# save_static_strategy2()
# print(static_user()['stock'])
# print(static_strategy1_info())