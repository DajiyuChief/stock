import sys
import numpy as np
import pandas as pd
import qdarkstyle
import pyqtgraph as pg
from datetime import date, datetime, timedelta
from mysql_link import MysqlData
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from login_ui import Ui_LoginWindow
from register_ui import Ui_RegisterWindow
from setting_ui import Ui_SettiingWindow
from select_stock_ui import Ui_SelectStockWindow
from select_stock_clhc import Ui_SelectStockHuiceWindow
from select_stock_k import Ui_SelectStockKgraphWindow
from select_stock_jyxx import  Ui_SelectStockJiaoyiInfoWindow
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from stock_frontend.trading_suggest import Ui_TradingSuggestWindow
from stock_frontend.trading_suggest_stocklist import Ui_TradingSuggestStockWindow
from trading_stock_backtest import Ui_TradingStockBacktestWindow
from select_ui import Ui_SelectWindow
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QHeaderView, QMessageBox

sys.path.append("./frontend_call_method/basic_info.py")
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from frontend_call_method import basic_info
from frontend_call_method import backtest_performance
from frontend_call_method import db_query
from frontend_call_method import real_time
from frontend_call_method import stock_pool

class MyLoginWindow(QMainWindow, Ui_LoginWindow):

    def __init__(self, parent=None):
        super(MyLoginWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.login_button)
        self.pushButton_2.clicked.connect(self.register_button)
        self.mydb = MysqlData("116.62.135.232", "root", "iamnts", "stock_db")
    def login_button(self):
        user_name = self.lineEdit.text()
        pwd = self.lineEdit_2.text()
        res = self.mydb.login(user_name, pwd)
        if res:
            print('ok')
            self.close()
            # self.win = SelectStockWindow()
            self.win=SelectWindow()
            self.win.show()
        else:
            QtWidgets.QMessageBox.warning(self, '错误', "请重新输入", buttons=QtWidgets.QMessageBox.Ok)
    def register_button(self):
        self.close()
        self.mianWin = RegMainWindow()
        self.mianWin.show()

class SelectWindow(QMainWindow,Ui_SelectWindow):
    def __init__(self,parent=None):
        super(SelectWindow,self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.on_click_1)
        self.pushButton_2.clicked.connect(self.on_click_2)
        self.pushButton_3.clicked.connect(self.on_click_3)
        self.pushButton_4.clicked.connect(self.on_click_4)
        # self.pushButton_5.clicked.connect(self.on_click_5)
        self.pushButton_6.clicked.connect(self.on_click_back)

    def on_click_back(self):
        self.close()
        self.win = MyLoginWindow()
        self.win.show()

    def on_click_1(self):
        self.close()
        # self.win=SelectStockWindow()
        self.win=TradingSuggestWindow()
        self.win.show()
    def on_click_2(self):
        self.close()
        # self.win =TransactionInforWindow()
        self.win=TradingSuggestStockWindow() # 交易推荐模块 股票列表
        self.win.show()
    def on_click_3(self):
        self.close()
        # self.win =SelectStockHuiceWindow()
        self.win=TradingBacktestWindow()
        self.win.show()
    def on_click_4(self):
        self.close()
        self.win =SettiingWindow()
        self.win.show()
    def on_click_5(self):
        self.close()
        self.win =KgraphWindow()
        self.win.show()

class RegMainWindow(QMainWindow, Ui_RegisterWindow):

    def __init__(self, parent=None):
        super(RegMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.mydb = MysqlData()#"116.62.135.232", "root", "root", "stock_db")
        self.pushButton.clicked.connect(self.ok_button)
        self.pushButton_2.clicked.connect(self.back_button)
        self.setWindowIcon(QtGui.QIcon('user.png'))
    def back_button(self):
        self.close()
        self.win = MyLoginWindow()
        self.win.show()
    def ok_button(self):
        self.close()
        user_name = self.lineEdit.text()
        user_pwd = self.lineEdit_2.text()
        user_pwd2 = self.lineEdit_3.text()
        if user_pwd != user_pwd2:
            QtWidgets.QMessageBox.warning(self, '错误', "密码不一致", buttons=QtWidgets.QMessageBox.Ok)
        else:
            self.mydb.register(user_name, user_pwd)
            QtWidgets.QMessageBox.warning(self, '提示', "注册成功！", buttons=QtWidgets.QMessageBox.Ok)
            self.back_button()

class KgraphWindow(QMainWindow, Ui_SelectStockKgraphWindow):
    def __init__(self):
        super(KgraphWindow, self).__init__()
        self.setupUi(self)
        self.k_plt = pg.PlotWidget(self.centralwidget)
        self.k_plt.setGeometry(QtCore.QRect(10, 260, 1131, 501))
        modes = ['1', '5', '15', '30', '60', '120', '日', '月']
        time_btns = [self.pushButton1min, self.pushButton5min, self.pushButton15min, self.pushButton30min,
                     self.pushButton60min, self.pushButton120min, self.pushButtonDay, self.pushButtonMonth]
        for i, btn in enumerate(time_btns):
            self.change_button_status(btn, modes[i])
        self.pushButtonRefresh.clicked.connect(self.open_setting)
        self.pushButtonReturn.clicked.connect(self.on_click_return)

    def on_click_return(self):
        self.close()
        self.win = SelectWindow()
        self.win.show()

    def open_setting(self):
        self.swin = SettiingWindow()
        self.swin.show()

    def change_button_status(self, btn, mode):
        btn.clicked.connect(lambda: self.label_TimeStatus.setText(mode))

class SelectStockWindow(QMainWindow, Ui_SelectStockWindow):
    def __init__(self):
        super(SelectStockWindow, self).__init__()
        self.setupUi(self)
        self.file_name = 'table_1.csv'
        self.creat_table_show()
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableWidget.cellPressed.connect(self.t_test)
        self.tableWidget.horizontalHeader().sectionClicked.connect(self.cell_sort)
        self.pushButtonReturn.clicked.connect(self.on_click_return)

    def on_click_return(self):
        self.close()
        self.win = SelectWindow()
        self.win.show()

    def cell_sort(self):
        col = self.tableWidget.selectedItems()[0].column()
        self.tableWidget.sortItems(col, Qt.DescendingOrder)

    def creat_table_show(self):
        if self.file_name:
            input_table = pd.read_csv(self.file_name, encoding='gbk')
            input_table_rows = input_table.shape[0]
            input_table_colunms = input_table.shape[1]
            input_table_header = input_table.columns.values.tolist()
            self.tableWidget.setColumnCount(7)
            self.tableWidget.setRowCount(input_table_rows)
            for i in range(input_table_rows):
                input_table_rows_values = input_table.iloc[[i]]
                input_table_rows_values_array = np.array(input_table_rows_values)
                input_table_rows_values_list = input_table_rows_values_array.tolist()[0]
                for j in range(input_table_colunms):
                    input_table_items_list = input_table_rows_values_list[j]
                    input_table_items = str(input_table_items_list)
                    newItem = QTableWidgetItem(input_table_items)
                    newItem.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                    self.tableWidget.setItem(i, j, newItem)
        else:
            self.centralWidget.show()

class SelectStockHuiceWindow(QMainWindow, Ui_SelectStockHuiceWindow):
    def __init__(self):
        super(SelectStockHuiceWindow, self).__init__()
        self.setupUi(self)
        modes = ['1','5','15','30','60','120','日','月']
        time_btns = [self.pushButton1min, self.pushButton5min, self.pushButton15min, self.pushButton30min,
                     self.pushButton60min, self.pushButton120min,self.pushButtonDay, self.pushButtonMonth]
        for i, btn in enumerate(time_btns):
            self.change_button_status(btn, modes[i])
        self.tableWidgetJixiao.horizontalHeader().sectionClicked.connect(lambda: self.cell_sort(self.tableWidgetJixiao))
        self.tableWidgetBaseInfo.horizontalHeader().sectionClicked.connect(lambda: self.cell_sort(self.tableWidgetBaseInfo))
        self.pushButtonReturn.clicked.connect(self.on_click_return)

    def on_click_return(self):
        self.close()
        self.win=SelectWindow()
        self.win.show()

    def cell_sort(self, obj):
        col = obj.selectedItems()[0].column()
        obj.sortItems(col, Qt.DescendingOrder)

    def change_button_status(self, btn, mode):
        btn.clicked.connect(lambda: self.label_TimeStatus.setText(mode))

class TransactionInforWindow(QMainWindow, Ui_SelectStockJiaoyiInfoWindow):
    def __init__(self):
        super(TransactionInforWindow, self).__init__()
        self.setupUi(self)
        self.tableWidgetJiaoyiInfo.horizontalHeader().sectionClicked.connect(self.cell_sort)
        modes = ['1', '5', '15', '30', '60', '120', '日', '月']
        time_btns = [self.pushButton1min, self.pushButton5min, self.pushButton15min, self.pushButton30min,
                     self.pushButton60min, self.pushButton120min, self.pushButtonDay, self.pushButtonMonth]
        for i, btn in enumerate(time_btns):
            self.change_button_status(btn, modes[i])
        self.pushButtonReturn.clicked.connect(self.on_click_return)

    def on_click_return(self):
        self.close()
        self.win = SelectWindow()
        self.win.show()

    def change_button_status(self, btn, mode):
        btn.clicked.connect(lambda: self.label_TimeStatus.setText(mode))

    def cell_sort(self):
        col = self.tableWidget.selectedItems()[0].column()
        self.tableWidgetJiaoyiInfo.sortItems(col, Qt.DescendingOrder)

class SettiingWindow(QMainWindow, Ui_SettiingWindow):
    def __init__(self):
        super(SettiingWindow, self).__init__()
        self.setupUi(self)
        self.pushButtonReturn.clicked.connect(self.on_click_return)
        self.pushButtonSetting.clicked.connect(self.on_click_output)
    def on_click_return(self):
        self.close()
        self.win = SelectWindow()
        self.win.show()
    def on_click_output(self):
        draw_kline(self.lineEdit5k.text(),self.lineEdit15k.text(),self.lineEdit30k.text(),self.lineEdit60k.text())
        QtWidgets.QMessageBox.warning(self, '正确', "导出成功", buttons=QtWidgets.QMessageBox.Ok)

class TradingBacktestWindow(QMainWindow, Ui_TradingStockBacktestWindow):
    span = 0
    def __init__(self):
        super(TradingBacktestWindow, self).__init__()
        self.setupUi(self)
        self.pushButtonOk.clicked.connect(self.beginBacktest)
        modes = ['30天','60天','120天','240天']
        time_btns = [self.pushButton30day, self.pushButton60day, self.pushButton120day, self.pushButton240day]
        for i, btn in enumerate(time_btns):
            self.change_button_status(btn, modes[i])
        self.tableWidgetBacktest.horizontalHeader().sectionClicked.connect(lambda: self.cell_sort(self.tableWidgetBacktest))
        self.tableWidgetBaseInfo.horizontalHeader().sectionClicked.connect(lambda: self.cell_sort(self.tableWidgetBaseInfo))
        self.pushButtonReturn.clicked.connect(self.on_click_return)

    def on_click_return(self):
        self.close()
        self.win = SelectWindow()
        self.win.show()
    def beginBacktest(self):
        stockcode = ""
        startday = ""
        endday = ""
        principal = 10000000
        isCharge = False
        isWhole = True
        percent = 0
        stop = 0.1
        type1 = False
        span = 0

        annual_yield = []

        if self.lineEditStockcode:
            stockcode = self.lineEditStockcode.text()
        if self.label_TimeStatus:
            span = self.label_TimeStatus.text()[:-1]
            span = int(span)
        if self.lineEditTimeStart:
            startday = self.lineEditTimeStart.text()
        if self.lineEditTimeEnd:
            endday = self.lineEditTimeEnd.text()
        if self.lineEditMACD:
            percent = self.lineEditMACD.text()
            percent = float(percent)
        if self.lineEditStop:
            stop = self.lineEditStop.text()
            stop = float(stop)
        if self.checkBoxAdd.isChecked():
            isWhole = False
        if self.rbtn1.isChecked():
            type1 = True
        if self.checkCharge.isChecked():
            isCharge = True
        if self.linePrincipal:
            principal = self.linePrincipal.text()
            principal = float(principal)
        if self.lineEditTimeStart and self.lineEditTimeEnd:
            annual_yield = backtest_performance.annual_yield_date(stockcode, startday, endday, principal, percent, stop, isCharge, type1, isWhole)
            start = datetime(int(startday[0:4]), int(startday[4:6]), int(startday[6:8]))
            end = datetime(int(endday[0:4]), int(endday[4:6]), int(endday[6:8]))
            span = (end - start).days
            self.label_TimeStatus.setText(str(span)+'天')
        elif self.label_TimeStatus:
            annual_yield = backtest_performance.annual_yield_span(stockcode, span, principal, percent, stop, isCharge, type1, isWhole)
            day = date.today()  # 当前日期
            now = datetime.now()
            delta = timedelta(span)
            n_days_forward = now - delta  # 当前日期向前推n天的时间
            startday = n_days_forward.strftime('%Y%m%d')
            endday = day.strftime('%Y%m%d')
        items = []
        lst = []
        lst.append(basic_info.getName(stockcode))
        lst.append(stockcode)
        lst.append(backtest_performance.priceChange(stockcode, startday, endday))
        tmp = annual_yield
        lst.append(tmp[0])
        lst.append(tmp[1])
        lst.append(backtest_performance.sharpe_ratio(stockcode, startday, endday))
        lst.append(backtest_performance.max_drawdown(stockcode, startday, endday))
        items.append(lst)
        for i in range(len(items)):
            item = items[i]
            row = self.tableWidgetBaseInfo.rowCount()
            self.tableWidgetBaseInfo.insertRow(row)
            for j in range(len(item)):
                item = QTableWidgetItem(str(items[i][j]))
                self.tableWidgetBaseInfo.setItem(row, j, item)
        if type1:
            items = db_query.list_for_strategy1()
        else:
            items = db_query.list_for_strategy2()
        for i in range(len(items)):
            item = items[i]
            row = self.tableWidgetBacktest.rowCount()
            self.tableWidgetBacktest.insertRow(row)
            for j in range(len(item)):
                item = QTableWidgetItem(str(items[i][j]))
                self.tableWidgetBacktest.setItem(row, j, item)

    def cell_sort(self, obj):
        col = obj.selectedItems()[0].column()
        obj.sortItems(col, Qt.DescendingOrder)

    def change_button_status(self, btn, mode):
        btn.clicked.connect(lambda: self.label_TimeStatus.setText(mode))


class TradingSuggestWindow(QMainWindow, Ui_TradingSuggestWindow):
    def __init__(self):
        super(TradingSuggestWindow, self).__init__()
        self.setupUi(self)
        self.pushButtonOk.clicked.connect(self.refresh)
        self.tableWidgetBacktest.horizontalHeader().sectionClicked.connect(lambda: self.cell_sort(self.tableWidgetBacktest))
        self.tableWidgetBaseInfo.horizontalHeader().sectionClicked.connect(lambda: self.cell_sort(self.tableWidgetBaseInfo))
        self.pushButtonReturn.clicked.connect(self.on_click_return)

    def on_click_return(self):
        self.close()
        self.win = SelectWindow()
        self.win.show()

    def refresh(self):
        stockcode = ""
        type1 = False
        percent = 0.1
        if self.lineEditStockcode:
            stockcode = self.lineEditStockcode.text()
        if self.lineEditMACD:
            percent = float(self.lineEditMACD.text())
        if self.rbtn1.isChecked():
            type1 = True
            if not stockcode == "":
                ans = real_time.suggest1(stockcode, percent)
                if ans[0]:
                    self.trade_type.setText('建议买入')
                elif ans[1]:
                    self.trade_type.setText('建议卖出')
                else:
                    self.trade_type.setText('建议不交易')
        elif self.rbtn2.isChecked():
            if not stockcode == "":
                ans = real_time.suggest2(stockcode, percent)
                if ans[0]:
                    self.trade_type.setText('建议买入')
                elif ans[1]:
                    self.trade_type.setText('建议卖出')
                else:
                    self.trade_type.setText('建议不交易')
        items = []
        get = real_time.get_real_time_data(stockcode)
        lst = []
        lst.append(get[0])
        lst.append(stockcode)
        lst.append(get[1])
        lst.append(get[2])
        lst.append(get[3])
        lst.append(get[4])
        lst.append(get[5])
        items.append(lst)
        for i in range(len(items)):
            item = items[i]
            row = self.tableWidgetBaseInfo.rowCount()
            self.tableWidgetBaseInfo.insertRow(row)
            for j in range(len(item)):
                item = QTableWidgetItem(str(items[i][j]))
                self.tableWidgetBaseInfo.setItem(row, j, item)
        if type1:
            items = stock_pool.static_strategy1_info()
        else:
            items = stock_pool.static_strategy2_info()
        for i in range(len(items)):
            item = items[i]
            row = self.tableWidgetBacktest.rowCount()
            self.tableWidgetBacktest.insertRow(row)
            for j in range(len(item)):
                item = QTableWidgetItem(str(items[i][j]))
                self.tableWidgetBacktest.setItem(row, j, item)

    def cell_sort(self, obj):
        col = obj.selectedItems()[0].column()
        obj.sortItems(col, Qt.DescendingOrder)

    def change_button_status(self, btn, mode):
        btn.clicked.connect(lambda: self.trade_type.setText(mode))


class TradingSuggestStockWindow(QMainWindow, Ui_TradingSuggestStockWindow):
    def __init__(self):
        super(TradingSuggestStockWindow, self).__init__()
        self.setupUi(self)
        self.rbtn1.setChecked(True)
        self.user()
        self.rbtn1.clicked.connect(self.user)
        self.rbtn2.clicked.connect(self.strategy1)
        self.rbtn3.clicked.connect(self.strategy2)
        self.tableWidgetBacktest.horizontalHeader().sectionClicked.connect(lambda: self.cell_sort(self.tableWidgetBacktest))

        self.pushButtonReturn.clicked.connect(self.on_click_return)

    def on_click_return(self):
        self.close()
        self.win = SelectWindow()
        self.win.show()
    def user(self):
        self.tableWidgetBacktest.setRowCount(0)
        self.tableWidgetBacktest.clearContents()
        items = stock_pool.static_user_stock_info()
        for i in range(len(items)):
            item = items[i]
            row = self.tableWidgetBacktest.rowCount()
            self.tableWidgetBacktest.insertRow(row)
            for j in range(len(item)):
                item = QTableWidgetItem(str(items[i][j]))
                self.tableWidgetBacktest.setItem(row, j, item)

    def strategy1(self):
        self.tableWidgetBacktest.setRowCount(0)
        self.tableWidgetBacktest.clearContents()
        try:
            items = stock_pool.static_strategy1_info()
        except Exception as e:
            print(e)
        for i in range(len(items)):
            item = items[i]
            row = self.tableWidgetBacktest.rowCount()
            self.tableWidgetBacktest.insertRow(row)
            for j in range(len(item)):
                item = QTableWidgetItem(str(items[i][j]))
                self.tableWidgetBacktest.setItem(row, j, item)

    def strategy2(self):
        self.tableWidgetBacktest.setRowCount(0)
        self.tableWidgetBacktest.clearContents()
        items = stock_pool.static_strategy2_info()
        for i in range(len(items)):
            item = items[i]
            row = self.tableWidgetBacktest.rowCount()
            self.tableWidgetBacktest.insertRow(row)
            for j in range(len(item)):
                item = QTableWidgetItem(str(items[i][j]))
                self.tableWidgetBacktest.setItem(row, j, item)

    def cell_sort(self, obj):
        col = obj.selectedItems()[0].column()
        obj.sortItems(col, Qt.DescendingOrder)

    def change_button_status(self, btn, mode):
        btn.clicked.connect(lambda: self.trade_type.setText(mode))

def draw_kline(ts_code,start_date='20210101',end_date='20220101',sep='daily'):
    from pyecharts.charts import Kline
    from pyecharts import options as opts
    import tushare as ts
    pro = ts.pro_api('f558cbc6b24ed78c2104e209a8a8986b33ec66b7c55bcfa2f46bc108')
    func={'daily':pro.daily,'weekly':pro.weekly,'monthly':pro.monthly}
    df=func[sep](**{
        "ts_code": ts_code,
        "trade_date": "",
        "start_date": start_date,
        "end_date": end_date,
        "offset": "",
        "limit": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "pre_close",
        "change",
        "pct_chg",
        "vol",
        "amount"
    ])
    return (
        Kline()
        .add_xaxis(df['trade_date'].values.tolist())
        .add_yaxis(
            "kline",
            df[['open','close','low','high']].values.tolist(),
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ec0000",
                color0="#00da3c",
                border_color="#8A0000",
                border_color0="#008F28",
            ),
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            datazoom_opts=[opts.DataZoomOpts(type_="inside")],
            title_opts=opts.TitleOpts(title=df['ts_code'][0]+'-'+df['trade_date'].values.tolist()[-1]+'-'+df['trade_date'].values.tolist()[0]+'-'+sep),
        )
        .render(df['ts_code'][0]+'-'+df['trade_date'].values.tolist()[-1]+'-'+df['trade_date'].values.tolist()[0]+'-'+sep+".html")
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    ui = MyLoginWindow()
    # ui = SelectStockWindow()
    # ui = SelectStockHuiceWindow()
    # ui = TransactionInforWindow()
    # ui = SettiingWindow()
    # ui = TradingBacktestWindow()
    # ui = TradingSuggestWindow()
    # ui = TradingSuggestStockWindow()
    ui.show()
    sys.exit(app.exec_())
