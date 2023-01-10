import sys
import os

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QUrl, QEventLoop, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow
from back import Ui_back
from menu import Ui_menu
from realtime import Ui_realtime
from recommend import Ui_recommend
from output import Ui_output
import easyquotation,numpy,pandas,tushare,talib,talib.stream,chinese_calendar
from data_modules import database_connection

class Menu(QMainWindow, Ui_menu):
    def __init__(self):
        super(Menu, self).__init__()
        self.setupUi(self)


class Realtime(QMainWindow, Ui_realtime):
    def __init__(self):
        super(Realtime, self).__init__()
        self.setupUi(self)
        # 设置按键功能
        # self.pushButton.clicked.connect(self.close)

    def Open(self):
        self.show()


class Back(QMainWindow, Ui_back):
    def __init__(self):
        super(Back, self).__init__()
        self.setupUi(self)
        # 设置按键功能
        # self.pushButton.clicked.connect(self.close)

    def Open(self):
        self.show()


class Recommend(QMainWindow, Ui_recommend):
    def __init__(self):
        super(Recommend, self).__init__()
        self.setupUi(self)
        # 设置按键功能
        # self.pushButton.clicked.connect(self.close)

    def Open(self):
        self.show()


class Klineshow(QMainWindow):
    def __init__(self):
        super(Klineshow, self).__init__()
        self.setWindowTitle('Kline')
        self.setGeometry(5, 30, 1390, 830)
        self.browser = QWebEngineView()
        # #加载外部的web界面
        url = os.getcwd() + os.path.sep + 'min_kline.html'
        self.browser.load(QUrl.fromLocalFile(url))
        self.setCentralWidget(self.browser)

    def Open(self):
        url = os.getcwd() + os.path.sep + 'min_kline.html'
        self.browser.load(QUrl.fromLocalFile(url))
        self.show()


class Klineshow_real(QMainWindow):
    def __init__(self):
        super(Klineshow_real, self).__init__()
        self.setWindowTitle('Kline')
        self.setGeometry(5, 30, 1390, 830)
        self.browser = QWebEngineView()
        # #加载外部的web界面
        url = os.getcwd() + os.path.sep + 'real_min_kline.html'
        self.browser.load(QUrl.fromLocalFile(url))
        self.setCentralWidget(self.browser)

    def Open(self):
        url = os.getcwd() + os.path.sep + 'real_min_kline.html'
        self.browser.load(QUrl.fromLocalFile(url))
        self.show()


class Output(QMainWindow, Ui_output):
    def __init__(self):
        super(Output, self).__init__()
        self.setupUi(self)
        # 设置按键功能
        # self.pushButton.clicked.connect(self.close)

    def Open(self):
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu = Menu()
    realtime = Realtime()
    back = Back()
    backcode = back.stockcode.toPlainText()
    recommend = Recommend()
    klineshow = Klineshow()
    klineshow_real = Klineshow_real()
    output = Output()
    menu.show()
    menu.realtime.clicked.connect(realtime.Open)
    menu.realtime.clicked.connect(output.Open)
    menu.back.clicked.connect(back.Open)
    menu.back.clicked.connect(output.Open)
    menu.recommend.clicked.connect(recommend.Open)
    # back.start.clicked.connect(output.Open)
    # output.kline.clicked.connect(klineshow.Open)
    # realtime.start.clicked.connect(output.Open)
    back.pushButton.clicked.connect(klineshow.Open)
    realtime.pushButton.clicked.connect(klineshow_real.Open)
    sys.exit(app.exec_())
