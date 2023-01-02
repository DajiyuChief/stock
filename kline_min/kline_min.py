import datetime

import efinance as ef
from pyecharts import options as opts
from pyecharts.charts import Kline, Bar, Grid, Line, Tab, Timeline
import tushare as ts
from getstockname import get_name
from kline_days import plot_kline_volume_signal
from data_modules import database_connection
import pandas as pd


def plot_kline(data, name) -> Kline:
    kline = (
        Kline(init_opts=opts.InitOpts(width="1800px", height="500px"))  # 设置画布大小
        .add_xaxis(xaxis_data=list(data.index))  # 将原始数据的index转化为list作为横坐标
        .add_yaxis(series_name="klines", y_axis=data[["开盘", "收盘", "最低", "最高"]].values.tolist(),
                   # 纵坐标采用OPEN、CLOSE、LOW、HIGH，注意顺序
                   itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c"), )
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
        width="1800px",
        height="1000px",
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
        buy.append(datetime.datetime.strptime(item,'%Y%m%d').strftime('%Y-%m-%d'))
    for item in sell_date:
        sell.append(datetime.datetime.strptime(item,'%Y%m%d').strftime('%Y-%m-%d'))
    return buy,buy_high,sell,sell_high



def generate_html():
    tab = Tab()
    stockcode = input("输入股票代码：")
    backtest = get_data_fromDB(stockcode)
    backstart = datetime.datetime.strptime(backtest['date'].values[0],'%Y%m%d').strftime('%Y-%m-%d')
    backend = datetime.datetime.strptime(backtest['date'].values[-1],'%Y%m%d').strftime('%Y-%m-%d')
    sell_buy = get_point_price(stockcode)
    stockcode = stockcode.split('.')[0]
    name = get_name(stockcode)
    today = datetime.date.today()
    offset = datetime.timedelta(days=-120)
    # 日期格式化
    finaldata = (today + offset).strftime('%Y-%m-%d')
    # df = ts.get_hist_data(stockcode, start=finaldata, end=str(today)).sort_index()  # 生成带有均线的日K图
    df_bak = ts.get_hist_data(stockcode, start=backstart, end=backend).sort_index()
    for freq in [5, 15, 30, 60]:  # 101为日代码
        data = ef.stock.get_quote_history(stockcode, klt=freq)  # 将数据按照时间排序
        data.set_index(["日期"], inplace=True)  # 设置日期为索引
        if freq != 101:
            tab.add(grid(data, name), str(freq) + "min")
        else:
            tab.add(grid(data, name), "日k")
    # tab.add(plot_kline_volume_signal(df, name), "日k")
    tab.add(plot_kline_volume_signal(df_bak,name,sell_buy),'回测日k')
    tab.render("min_kline.html")
