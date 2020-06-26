# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\jonson\Dropbox\0_回家作業\finance_public\QTdesign.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import twstock
import test_台股_update
import test_台股_不停損投資模型



class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1259, 606)
        self.stockID = QtWidgets.QLineEdit(Dialog)
        self.stockID.setEnabled(True)
        self.stockID.setGeometry(QtCore.QRect(203, 21, 235, 30))
        self.stockID.setObjectName("stockID")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(71, 21, 120, 24))
        self.label.setObjectName("label")
        self.Btm_update_stock = QtWidgets.QPushButton(Dialog)
        self.Btm_update_stock.setGeometry(QtCore.QRect(29, 140, 181, 46))
        self.Btm_update_stock.setObjectName("Btm_update_stock")
        self.Btm_noStop = QtWidgets.QPushButton(Dialog)
        self.Btm_noStop.setGeometry(QtCore.QRect(250, 140, 150, 46))
        self.Btm_noStop.setObjectName("Btm_noStop")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(510, 30, 168, 24))
        self.label_2.setObjectName("label_2")
        self.calendarWidget = QtWidgets.QCalendarWidget(Dialog)
        self.calendarWidget.setGeometry(QtCore.QRect(700, 20, 440, 360))
        self.calendarWidget.setObjectName("calendarWidget")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

#按鈕事件
        self.Btm_update_stock.clicked.connect(self.Btm_update_stock_presss)   
        self.Btm_noStop.clicked.connect(self.Btm_noStop_press)
        
        
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.stockID.setText(_translate("Dialog", "0050"))
        self.label.setText(_translate("Dialog", "股票代號："))
        self.Btm_update_stock.setText(_translate("Dialog", "更新股價數據"))
        self.Btm_noStop.setText(_translate("Dialog", "不停損模型"))
        self.label_2.setText(_translate("Dialog", "分析開始時間："))
        
    def Btm_update_stock_presss(self):
        print('\r\nBtm_update_stock_process 開始')
        sid = self.stockID.text()
        print(twstock.codes[sid].name)
        test_台股_update.check_history_data(sid)
        test_台股_update.caculate_model(sid, 20)
        print('Btm_update_stock_process 結束')
        
    def Btm_noStop_press(self):
        print('\r\nBtm_noStop_press 開始')
        sid = self.stockID.text()
        date=self.calendarWidget.selectedDate()
        print(twstock.codes[sid].name)
        test_台股_不停損投資模型.caculate_model(sid, 20,"台灣50",date.toString("yyyy/MM/dd"),adj_fix=False)
        print('Btm_noStop_press 結束')

        
if __name__ == '__main__':  
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_Dialog()

    ui.setupUi(MainWindow) 
    MainWindow.show()
    sys.exit(app.exec_()) 
