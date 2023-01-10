import datetime

import efinance as ef
import pandas as pd
import tushare as ts
from pyecharts import options as opts
from pyecharts.charts import Kline, Bar, Grid, Tab

from data_modules import database_connection, gol
from getstockname import get_name
from kline_days import plot_kline_volume_signal
from trading_strategy_2.backtest2 import realtime, date_backtest2

# 显示所有行
pd.set_option('display.max_rows', 1000)
# 显示所有列
pd.set_option('display.max_columns', 1000)
pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')


def plot_kline(data, name) -> Kline:
    kline = (
        Kline(init_opts=opts.InitOpts(width="1800px", height="500px"))  # 设置画布大小
        .add_xaxis(xaxis_data=list(data.index))  # 将原始数据的index转化为list作为横坐标
        .add_yaxis(series_name="klines", y_axis=data[["开盘", "收盘", "最低", "最高"]].values.tolist(),
                   itemstyle_opts=opts.ItemStyleOpts(color="#c61328", color0="#223b24"),)
                   # 纵坐标采用OPEN、CLOSE、LOW、HIGH，注意顺序
                   # itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c"),
        .set_global_opts(legend_opts=opts.LegendOpts(is_show=True, pos_bottom=10, pos_left="center"),
                         datazoom_opts=[
                             opts.DataZoomOpts(
                                 is_show=False,
                                 type_="inside",
                                 xaxis_index=[0, 1],
                                 range_start=98,
                                 range_end=100,
                             ),
                             opts.DataZoomOpts(
                                 is_show=True,
                                 xaxis_index=[0],
                                 type_="slider",
                                 pos_top="85%",
                                 range_start=98,
                                 range_end=100,
                             ),
                         ],
                         yaxis_opts=opts.AxisOpts(
                             is_scale=True,
                             splitarea_opts=opts.SplitAreaOpts(
                                 is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                             ),
                         ),
                         tooltip_opts=opts.TooltipOpts(
                             trigger="axis",
                             axis_pointer_type="cross",
                             background_color="rgba(245, 245, 245, 0.8)",
                             border_width=1,
                             border_color="#ccc",
                             textstyle_opts=opts.TextStyleOpts(color="#000"),
                         ),
                         visualmap_opts=opts.VisualMapOpts(
                             is_show=False,
                             dimension=2,
                             series_index=5,
                             is_piecewise=True,
                             pieces=[
                                 {"value": 1, "color": "#00da3c"},
                                 {"value": -1, "color": "#ec0000"},
                             ],
                         ),
                         axispointer_opts=opts.AxisPointerOpts(
                             is_show=True,
                             link=[{"xAxisIndex": "all"}],
                             label=opts.LabelOpts(background_color="#777"),
                         ),
                         brush_opts=opts.BrushOpts(
                             x_axis_index="all",
                             brush_link="all",
                             out_of_brush={"colorAlpha": 0.1},
                             brush_type="lineX",
                         ),
                         title_opts=opts.TitleOpts(
                             title=name,
                             pos_left='center',
                             title_textstyle_opts=opts.TextStyleOpts(
                                 font_size=30
                             )
                         )
                         )
    )
    return kline


def volume_bar(data) -> Bar:
    # 计算价格变动
    data['价格变动'] = data['收盘'] - data['开盘']
    ups = data.where(data['价格变动'] > 0, 0)['成交量']
    downs = data.where(~(data['价格变动'] > 0), 0)['成交量']
    bar = (
        Bar()
        .add_xaxis(xaxis_data=list(data.index))
        .add_yaxis(
            series_name='交易量',
            y_axis=ups.values.tolist(),
            xaxis_index=1,
            yaxis_index=1,
            gap='-100%',
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color='#ef232a')
        )
        .add_yaxis(
            series_name='交易量',
            y_axis=downs.values.tolist(),
            xaxis_index=1,
            yaxis_index=1,
            gap='-100%',
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color='#14b143')
        )
    )

    bar.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            type_="category",
            grid_index=1,
            axislabel_opts=opts.LabelOpts(is_show=False),
        ),
        legend_opts=opts.LegendOpts(is_show=False),
    )
    return bar


def grid(data, name) -> Grid:
    grid_chart = Grid(init_opts=opts.InitOpts(
        width="1350px",
        height="750px",
        animation_opts=opts.AnimationOpts(animation=False), ))
    kline = plot_kline(data, name)
    bar = volume_bar(data)
    grid_chart.add(
        kline,
        grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", height="40%"),
    ),
    grid_chart.add(
        bar,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top="60%", height="20%"
        ),
    ),
    return grid_chart


# 从数据库获取所需数据
def get_data_fromDB(stockcode):
    db = database_connection.MySQLDb()
    sql = "select * from backtest2 where code = '%s'" % str(stockcode)
    df = pd.DataFrame(db.select_all(sql))
    return df


def get_real_data_fromDB(stockcode):
    db = database_connection.MySQLDb()
    sql = "select * from actual2 where code = '%s'" % str(stockcode)
    df = pd.DataFrame(db.select_all(sql))
    return df


# 从数据库获取的数据中提取买卖点日期和价格
def get_point_price(stockcode):
    buy = []
    sell = []
    backtest = get_data_fromDB(stockcode)
    buy_data = backtest[backtest['type'] == 1]
    sell_data = backtest[backtest['type'] == 0]
    buy_date = buy_data['date'].values.tolist()
    buy_high = buy_data['high'].values.tolist()
    sell_date = sell_data['date'].values.tolist()
    sell_high = sell_data['high'].values.tolist()
    for item in buy_date:
        buy.append(datetime.datetime.strptime(item, '%Y%m%d').strftime('%Y-%m-%d'))
    for item in sell_date:
        sell.append(datetime.datetime.strptime(item, '%Y%m%d').strftime('%Y-%m-%d'))
    return buy, buy_high, sell, sell_high


def get_real_point_price(stockcode):
    buy = []
    sell = []
    backtest = get_real_data_fromDB(stockcode)
    buy_data = backtest[backtest['type'] == 1]
    sell_data = backtest[backtest['type'] == 0]
    buy_date = buy_data['date'].values.tolist()
    buy_high = buy_data['high'].values.tolist()
    sell_date = sell_data['date'].values.tolist()
    sell_high = sell_data['high'].values.tolist()
    for item in buy_date:
        buy.append(datetime.datetime.strptime(item, '%Y%m%d').strftime('%Y-%m-%d'))
    for item in sell_date:
        sell.append(datetime.datetime.strptime(item, '%Y%m%d').strftime('%Y-%m-%d'))
    return buy, buy_high, sell, sell_high


def setdata(start_day, end_day, stock_code):
    df = pro.daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
    if len(df) == 0:
        df = pro.fund_daily(ts_code=stock_code, start_date=start_day, end_date=end_day)
    if len(df) == 0:
        print('无法获取相关数据')
        return
    df = df.sort_values(by='trade_date', ascending=True)
    return df


def cal_ma(df):
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    return df



def get_backdate_ma(stockcode, start, end):
    glo_data = gol.get_value(stockcode)
    df = setdata(start, end, stockcode)
    strat_date = df['trade_date'].values.tolist()[0]
    end_date = df['trade_date'].values.tolist()[-1]
    start_index = glo_data[glo_data['trade_date'] == strat_date].index[0] + 1
    end_index = glo_data[glo_data['trade_date'] == end_date].index[0]
    df = glo_data[-start_index:-end_index]
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df['trade_date'], format='%Y-%m-%d')
    df_copy2 = df_copy.copy()
    df_copy2['date'] = df_copy['date'].astype(str)
    df_copy2 = df_copy2.set_index('date')
    df_copy2['volume'] = df_copy2['vol']
    return df_copy2


def get_realdata_ma(stockcode, days):
    # ma数据需要前几日数据计算，故多取几日数据后截取
    glo_data = gol.get_value(stockcode).reset_index(drop=True)
    # today = datetime.date.today()
    # offset = datetime.timedelta(days=-days)
    # finaldata = today + offset
    # today_ymd_str = datetime.datetime.strftime(today, '%Y%m%d')
    # strat_ymd_str = datetime.datetime.strftime(finaldata, '%Y%m%d')
    # df = setdata(strat_ymd_str, today_ymd_str, stockcode).reset_index(drop=True)
    # strat_date = df['trade_date'].values.tolist()[0]
    # start_index = glo_data[glo_data['trade_date'] == strat_date].index[0] + 1
    # print(strat_date, start_index)
    df = glo_data[-days:]
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df['trade_date'], format='%Y-%m-%d')
    df_copy2 = df_copy.copy()
    df_copy2['date'] = df_copy['date'].astype(str)
    df_copy2 = df_copy2.set_index('date')
    df_copy2['volume'] = df_copy2['vol']
    # print(df_copy2)
    return df_copy2


def generate_html(stockcode, start, end):
    tab = Tab()
    # stockcode = input("输入股票代码：")
    stockcodebak = stockcode
    backtest = get_data_fromDB(stockcode)
    # df_back = get_backdate_ma(stockcode, backtest['date'].values[0], backtest['date'].values[-1])
    df_back = get_backdate_ma(stockcode, start, end)
    # backstart = datetime.datetime.strptime(backtest['date'].values[0], '%Y%m%d').strftime('%Y-%m-%d')
    # backend = datetime.datetime.strptime(backtest['date'].values[-1], '%Y%m%d').strftime('%Y-%m-%d')
    sell_buy = get_point_price(stockcode)
    # stockcode = stockcode.split('.')[0]
    # print(stockcode)
    name = get_name(stockcode)
    # df = ts.get_hist_data(stockcode, start=finaldata, end=str(today)).sort_index()  # 生成带有均线的日K图
    # df_bak = ts.get_hist_data(stockcode, start=backstart, end=backend).sort_index()
    # print(df_bak)
    for freq in [5, 15, 30, 60]:  # 101为日代码
        data = ef.stock.get_quote_history(stockcode.split('.')[0], klt=freq)  # 将数据按照时间排序
        data.set_index(["日期"], inplace=True)  # 设置日期为索引
        if freq != 101:
            tab.add(grid(data, name), str(freq) + "min")
        else:
            tab.add(grid(data, name), "日k")
    # tab.add(plot_kline_volume_signal(df, name), "日k")
    tab.add(plot_kline_volume_signal(df_back, name, sell_buy), '回测日k')
    tab.render("min_kline.html")
    # tab.render(stockcodebak+"min_kline.html")
    print('k线图已生成')


def generate_real_html(stockcode, days):
    tab = Tab()
    # stockcodebak = stockcode
    df_real = get_realdata_ma(stockcode, days)
    sell_buy = get_real_point_price(stockcode)
    # stockcode = stockcode.split('.')[0]
    # print(stockcode)
    name = get_name(stockcode)
    # today = datetime.date.today()
    # offset = datetime.timedelta(days=-120)
    # finaldata = today + offset
    # df = ts.get_hist_data(stockcode, start=str(finaldata), end=str(today)).sort_index()  # 生成带有均线的日K图
    # df_bak = ts.get_hist_data(stockcode, start=backstart, end=backend).sort_index()
    for freq in [5, 15, 30, 60]:  # 101为日代码
        data = ef.stock.get_quote_history(stockcode.split('.')[0], klt=freq)  # 将数据按照时间排序
        data.set_index(["日期"], inplace=True)  # 设置日期为索引
        if freq != 101:
            tab.add(grid(data, name), str(freq) + "min")
        else:
            tab.add(grid(data, name), "日k")
    tab.add(plot_kline_volume_signal(df_real, name, sell_buy), "日k")
    # tab.add(plot_kline_volume_signal(df_bak, name, sell_buy), '回测日k')
    tab.render("real_min_kline.html")
    # tab.render(stockcodebak+"min_kline.html")
    print('k线图已生成')


# date_backtest2('20220325', '20220614', '600073.SH', 9999999, 0.1, 0.3, False, True)
# generate_html('600073.SH','20220325', '20220614')
# realtime('600073.SH', 9999999, 0.1, 0.3, False, True, 60)
# generate_real_html('600073.SH',60)
