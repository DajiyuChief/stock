# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'select_stock_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SelectStockWindow(object):
    def setupUi(self, SelectStockWindow):
        SelectStockWindow.setObjectName("SelectStockWindow")
        SelectStockWindow.resize(1148, 769)
        SelectStockWindow.setToolTip("")
        SelectStockWindow.setStatusTip("")
        self.centralwidget = QtWidgets.QWidget(SelectStockWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 110, 1131, 651))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.tableWidget.setFont(font)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(False)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.verticalHeader().setSortIndicatorShown(False)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 50, 511, 32))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setMaximumSize(QtCore.QSize(96, 16777215))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit.setMinimumSize(QtCore.QSize(97, 0))
        self.lineEdit.setMaximumSize(QtCore.QSize(97, 16777215))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.lineEdit.setFont(font)
        self.lineEdit.setToolTip("")
        self.lineEdit.setStatusTip("")
        self.lineEdit.setWhatsThis("")
        self.lineEdit.setInputMask("")
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.comboBox = QtWidgets.QComboBox(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.comboBox.setFont(font)
        self.comboBox.setProperty("placeholderText", "")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout.addWidget(self.comboBox)
        self.comboBox_2 = QtWidgets.QComboBox(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.comboBox_2.setFont(font)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.horizontalLayout.addWidget(self.comboBox_2)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(510, 0, 110, 102))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox = QtWidgets.QCheckBox(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.checkBox.setFont(font)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.addWidget(self.checkBox)
        self.checkBox_2 = QtWidgets.QCheckBox(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.checkBox_2.setFont(font)
        self.checkBox_2.setAutoFillBackground(False)
        self.checkBox_2.setChecked(True)
        self.checkBox_2.setAutoRepeat(False)
        self.checkBox_2.setAutoExclusive(False)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout.addWidget(self.checkBox_2)
        self.checkBox_3 = QtWidgets.QCheckBox(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.checkBox_3.setFont(font)
        self.checkBox_3.setObjectName("checkBox_3")
        self.verticalLayout.addWidget(self.checkBox_3)
        self.layoutWidget2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget2.setGeometry(QtCore.QRect(620, 40, 521, 41))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_2.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.layoutWidget2)
        self.lineEdit_2.setMaximumSize(QtCore.QSize(120, 16777215))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_2.addWidget(self.lineEdit_2)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.layoutWidget2)
        self.lineEdit_3.setMaximumSize(QtCore.QSize(120, 16777215))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.lineEdit_3.setFont(font)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout_2.addWidget(self.lineEdit_3)
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget2)
        self.pushButton.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.layoutWidget2)
        self.pushButton_2.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.pushButtonReturn = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonReturn.setGeometry(QtCore.QRect(10, 10, 161, 31))
        self.pushButtonReturn.setObjectName("pushButtonReturn")
        SelectStockWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(SelectStockWindow)
        QtCore.QMetaObject.connectSlotsByName(SelectStockWindow)

    def retranslateUi(self, SelectStockWindow):
        _translate = QtCore.QCoreApplication.translate
        SelectStockWindow.setWindowTitle(_translate("SelectStockWindow", "股票池-选股"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("SelectStockWindow", "全部选中"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("SelectStockWindow", "行业"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("SelectStockWindow", "股票代码"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("SelectStockWindow", "股票名称"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("SelectStockWindow", "市盈率得分"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("SelectStockWindow", "财务得分"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("SelectStockWindow", "总分"))
        self.label.setText(_translate("SelectStockWindow", "测试日期:"))
        self.lineEdit.setPlaceholderText(_translate("SelectStockWindow", "2021-01-05"))
        self.comboBox.setItemText(0, _translate("SelectStockWindow", "全部行业分级"))
        self.comboBox.setItemText(1, _translate("SelectStockWindow", "L1"))
        self.comboBox.setItemText(2, _translate("SelectStockWindow", "L2"))
        self.comboBox.setItemText(3, _translate("SelectStockWindow", "L3"))
        self.comboBox_2.setItemText(0, _translate("SelectStockWindow", "全部行业分类"))
        self.checkBox.setText(_translate("SelectStockWindow", "是否新股"))
        self.checkBox_2.setText(_translate("SelectStockWindow", "是否ST"))
        self.checkBox_3.setText(_translate("SelectStockWindow", "是否停牌"))
        self.label_2.setText(_translate("SelectStockWindow", "市值范围:"))
        self.lineEdit_2.setPlaceholderText(_translate("SelectStockWindow", "亿"))
        self.lineEdit_3.setPlaceholderText(_translate("SelectStockWindow", "亿"))
        self.pushButton.setText(_translate("SelectStockWindow", "确认"))
        self.pushButton_2.setText(_translate("SelectStockWindow", "设置"))
        self.pushButtonReturn.setText(_translate("SelectStockWindow", "返回主界面"))
