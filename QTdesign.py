# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\jonson\Dropbox\0_回家作業\finance_public\QTdesign.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate, QDateTime
import sys
import twstock
import test_台股_update
import test_台股_不停損投資模型
import json
import datetime
import time

from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)

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
        self.Btm_update_stock_2 = QtWidgets.QPushButton(Dialog)
        self.Btm_update_stock_2.setGeometry(QtCore.QRect(30, 210, 181, 46))
        self.Btm_update_stock_2.setObjectName("Btm_update_stock_2")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

#按鈕事件
        self.Btm_update_stock.clicked.connect(self.Btm_update_stock_presss)   
        self.Btm_update_stock_2.clicked.connect(self.Btm_update_stock_2_presss)   
        self.Btm_noStop.clicked.connect(self.Btm_noStop_press)
        
        self.config_load()
        
        
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "炒股賺錢勿忘本人大恩大德，炒股賠錢一律與本人無關"))
        self.stockID.setText(_translate("Dialog", "0050"))
        self.label.setText(_translate("Dialog", "股票代號："))
        self.Btm_update_stock.setText(_translate("Dialog", "更新「台股」數據"))
        self.Btm_noStop.setText(_translate("Dialog", "不停損模型"))
        self.label_2.setText(_translate("Dialog", "分析開始時間："))
        self.Btm_update_stock_2.setText(_translate("Dialog", "更新「美股」數據"))
        
        
    def Btm_update_stock_presss(self):
        print('\r\n更新「台股」歷史資料 開始')
        sid = self.stockID.text()
        try:
            print(twstock.codes[sid].name)
            test_台股_update.check_history_data(sid)
            test_台股_update.caculate_model(sid, 20)
            print('更新股價歷史資料 結束')
        except:
            print("\r\bError: 請確認網路連線，或是股價代碼。歷史數據至少要2015年起")

        
    def Btm_update_stock_2_presss(self):
        print('\r\n更新「美股」歷史資料 開始')
        sid = self.stockID.text()
        n_year = 15

        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        # n 年的資料
        start_date = (datetime.datetime.now()- datetime.timedelta(days=n_year*365)).strftime('%Y-%m-%d')
        SID = sid
        out_file = "測試資料/台股/{0}d.csv".format(SID)
        



        # 日K 資料
        data = pdr.get_data_yahoo(SID, start=start_date, end=end_date)


        print(len(data.index.values))
        data.to_csv(out_file, sep=',', encoding='utf-8')


        # download Panel
        #= pdr.get_data_yahoo(["SPY", "IWM"], start="2017-01-01", end="2017-04-30")
        #print(data3)
        time.sleep(3)

        print('更新股價歷史資料 結束')
 
        

        
    def Btm_noStop_press(self):
        print('\r\n不停損策略 開始')
        sid = self.stockID.text()
        date=self.calendarWidget.selectedDate()
        try:
            print("{0}, 啟始時間：{1}".format(twstock.codes[sid].name , date.toString("yyyy/MM/dd")))
            test_台股_不停損投資模型.caculate_model(sid, 20,"台灣50",date.toString("yyyy/MM/dd"),adj_fix=False)
        except:
            # 資料來源為yahoo, 使用還原數據
            print("{0}, 啟始時間：{1}".format(" " , date.toString("yyyy/MM/dd")))        
            test_台股_不停損投資模型.caculate_model(sid, 20,"台灣50",date.toString("yyyy/MM/dd"),adj_fix=True)
        
        self.config_save()
        print('不停損策略 結束')
        
    def config_load(self):
        #讀取設定檔
        print("load")
        f = open('config_QTdesign.json', "r",  encoding='UTF-8')
        self.Configs = json.loads(f.read())
        f.close()
        
        _translate = QtCore.QCoreApplication.translate
        self.stockID.setText(_translate("Dialog", self.Configs['sid']))
        
        qday = QDate.fromString(self.Configs['test_start_date'], "yyyy/MM/dd")
        self.calendarWidget.setSelectedDate(qday)

    
    def config_save(self):
        print("save")
        sid = self.stockID.text()
        date=self.calendarWidget.selectedDate()
        
        self.Configs['sid'] = sid
        self.Configs['test_start_date'] = date.toString("yyyy/MM/dd")
        
        ret = json.dumps(self.Configs)
        
        f = open('config_QTdesign.json', "w",  encoding='UTF-8')
        f.write(ret)
        f.close()
        
if __name__ == '__main__':  
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_Dialog()
    ui.setupUi(MainWindow) 
    MainWindow.show()
    sys.exit(app.exec_()) 
