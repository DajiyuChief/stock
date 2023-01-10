# 将html通过QtWebEngine展示
import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from kline_min import generate_html


class MainWindow(QMainWindow):
    def __init__(self, stockcode):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Kline')
        self.setGeometry(5, 30, 1850, 1100)
        self.browser = QWebEngineView()
        # #加载外部的web界面
        url = os.getcwd() + os.path.sep + stockcode + 'min_kline.html'
        self.browser.load(QUrl.fromLocalFile(url))
        self.setCentralWidget(self.browser)


def show_kline(stockcode):
    # generate_html()
    app = QApplication(sys.argv)
    win = MainWindow(stockcode)
    win.show()
    sys.exit(app.exec_())
    # app.exit(app.exec_())


# show_kline()
