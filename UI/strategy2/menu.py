# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'menu.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_menu(object):
    def setupUi(self, menu):
        menu.setObjectName("menu")
        menu.resize(372, 172)
        menu.setMinimumSize(QtCore.QSize(372, 172))
        menu.setMaximumSize(QtCore.QSize(372, 172))
        self.centralwidget = QtWidgets.QWidget(menu)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 40, 331, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.recommend = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.recommend.setObjectName("recommend")
        self.horizontalLayout.addWidget(self.recommend)
        self.realtime = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.realtime.setObjectName("realtime")
        self.horizontalLayout.addWidget(self.realtime)
        self.back = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.back.setObjectName("back")
        self.horizontalLayout.addWidget(self.back)
        menu.setCentralWidget(self.centralwidget)

        self.retranslateUi(menu)
        QtCore.QMetaObject.connectSlotsByName(menu)

    def retranslateUi(self, menu):
        _translate = QtCore.QCoreApplication.translate
        menu.setWindowTitle(_translate("menu", "策略二"))
        self.recommend.setText(_translate("menu", "查看推荐股票（未完成）"))
        self.realtime.setText(_translate("menu", "实时"))
        self.back.setText(_translate("menu", "回测"))

        
