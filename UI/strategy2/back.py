# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'back.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from trading_strategy_2.backtest2 import date_backtest2
from data_modules import gol
import sys
from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from kline_min import generate_html

class Ui_back(object):
    def setupUi(self, back):
        back.setObjectName("back")
        back.resize(220, 600)
        back.setMinimumSize(QtCore.QSize(220, 600))
        back.setMaximumSize(QtCore.QSize(220, 600))
        # back.move(100,50)
        self.centralwidget = QtWidgets.QWidget(back)
        self.centralwidget.setObjectName("centralwidget")
        self.stockcode = QtWidgets.QTextEdit(self.centralwidget)
        self.stockcode.setGeometry(QtCore.QRect(30, 10, 161, 31))
        self.stockcode.setObjectName("stockcode")
        self.starttime = QtWidgets.QTextEdit(self.centralwidget)
        self.starttime.setGeometry(QtCore.QRect(30, 60, 161, 31))
        self.starttime.setObjectName("starttime")
        self.endtime = QtWidgets.QTextEdit(self.centralwidget)
        self.endtime.setGeometry(QtCore.QRect(30, 110, 161, 31))
        self.endtime.setObjectName("endtime")
        self.condition1rsi = QtWidgets.QTextEdit(self.centralwidget)
        self.condition1rsi.setGeometry(QtCore.QRect(30, 160, 161, 31))
        self.condition1rsi.setObjectName("condition1rsi")
        self.spbuyrsi = QtWidgets.QTextEdit(self.centralwidget)
        self.spbuyrsi.setGeometry(QtCore.QRect(30, 210, 161, 31))
        self.spbuyrsi.setObjectName("spbuyrsi")
        self.spsellrsi = QtWidgets.QTextEdit(self.centralwidget)
        self.spsellrsi.setGeometry(QtCore.QRect(30, 260, 161, 31))
        self.spsellrsi.setObjectName("spsellrsi")
        self.principal = QtWidgets.QTextEdit(self.centralwidget)
        self.principal.setGeometry(QtCore.QRect(30, 310, 161, 31))
        self.principal.setMarkdown("")
        self.principal.setObjectName("principal")
        self.stoploss = QtWidgets.QTextEdit(self.centralwidget)
        self.stoploss.setGeometry(QtCore.QRect(30, 360, 161, 31))
        self.stoploss.setObjectName("stoploss")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(30, 420, 161, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.start = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.start.setObjectName("start")
        self.horizontalLayout.addWidget(self.start)
        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        # self.output = QtWidgets.QTextBrowser(self.centralwidget)
        # self.output.setGeometry(QtCore.QRect(220, 10, 561, 551))
        # self.output.setObjectName("output")
        self.condition1rsi.raise_()
        self.spbuyrsi.raise_()
        self.principal.raise_()
        self.stoploss.raise_()
        self.stockcode.raise_()
        self.spsellrsi.raise_()
        self.starttime.raise_()
        self.endtime.raise_()
        self.horizontalLayoutWidget.raise_()
        # self.output.raise_()
        back.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(back)
        self.statusbar.setObjectName("statusbar")
        back.setStatusBar(self.statusbar)

        # 允许tab切换
        self.stockcode.setTabChangesFocus(True)
        self.starttime.setTabChangesFocus(True)
        self.endtime.setTabChangesFocus(True)
        self.condition1rsi.setTabChangesFocus(True)
        self.spbuyrsi.setTabChangesFocus(True)
        self.spsellrsi.setTabChangesFocus(True)
        self.principal.setTabChangesFocus(True)
        self.stoploss.setTabChangesFocus(True)

        # 设置默认值
        self.stockcode.setPlainText('600073.SH')
        self.starttime.setPlainText('20220325')
        self.endtime.setPlainText('20220614')
        self.condition1rsi.setPlainText('0.1')
        self.spbuyrsi.setPlainText('0.2')
        self.spsellrsi.setPlainText('0.1')
        self.principal.setPlainText('9999999')
        self.stoploss.setPlainText('0.3')

        # self.stockcode.setPlaceholderText('股票代码如：600073.SH')
        # self.starttime.setPlaceholderText('开始时间如：20220325')
        # self.endtime.setPlaceholderText('结束时间如：20220614')
        # self.condition1rsi.setPlaceholderText('买卖条件一rsi如：0.1')
        # self.spbuyrsi.setPlaceholderText('特殊买条件rsi如：0.2')
        # self.spsellrsi.setPlaceholderText('特殊卖条件rsi如：0.1')
        # self.principal.setPlaceholderText('资金如：9999999')
        # self.stoploss.setPlaceholderText('止损率如：0.3')

        self.start.clicked.connect(self.run)
        # sys.stdout = EmittingStr(textWritten=self.outputWritten)
        # sys.stderr = EmittingStr(textWritten=self.outputWritten)

        self.retranslateUi(back)
        QtCore.QMetaObject.connectSlotsByName(back)

    def retranslateUi(self, back):
        _translate = QtCore.QCoreApplication.translate
        back.setWindowTitle(_translate("back", "回测"))
        self.start.setText(_translate("back", "回测"))
        self.pushButton.setText(_translate("back", "k线图"))

    # def outputWritten(self, text):
    #     cursor = self.output.textCursor()
    #     cursor.movePosition(QtGui.QTextCursor.End)
    #     cursor.insertText(text)
    #     self.output.setTextCursor(cursor)
    #     self.output.ensureCursorVisible()

    def run(self):
        code = self.stockcode.toPlainText()
        start = self.starttime.toPlainText()
        end = self.endtime.toPlainText()
        condition_rsi = float(self.condition1rsi.toPlainText())
        special_buy_rsi = float(self.spbuyrsi.toPlainText())
        special_sell_rsi = float(self.spsellrsi.toPlainText())
        principal = float(self.principal.toPlainText())
        stoploss = float(self.stoploss.toPlainText())
        gol.set_value('special_buy_rsi',special_buy_rsi)
        gol.set_value('special_sell_rsi',special_sell_rsi)
        date_backtest2(start,end,code,principal,condition_rsi,stoploss,False,True)
        generate_html(code,start,end)


# class EmittingStr(QtCore.QObject):
#     textWritten = QtCore.pyqtSignal(str) #定义一个发送str的信号
#     def write(self, text):
#       self.textWritten.emit(str(text))
#       loop = QEventLoop()
#       QTimer.singleShot(10, loop.quit)
#       loop.exec_()