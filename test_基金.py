# -*- coding: utf-8 -*-
import numpy as np
import sys
from stock import stock
from stock import stock_5day
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

            
if __name__ == '__main__':
    #s = stock("D:/Dropbox/0_回家作業/finance/測試資料/基金/天達環球策略基金 - 環球黃金基金 C 收益股份.csv")
    s = stock("測試資料/基金/{0}.csv".format(sys.argv[1]))
    period = 260 # 一年約有 263 個資料。
    date, data = s.feature_Annualized(1, period)
    date3, data3 = s.feature_Annualized(3, period)
    date4, data4 = s.feature_Annualized(4, period)
    date5, data5 = s.feature_Annualized(5, period)
    date10, data10 = s.feature_Annualized(10, period)

    print("{0} {1} {2}".format(round(np.average(data),2),round(np.std(data),2),round(np.min(data),2)))
    if len(data3) >0 :
        print("{0} {1} {2}".format(round(np.average(data3),2),round(np.std(data3),2),round(np.min(data3),2)))
    if len(data5) >0 :
        print("{0} {1} {2}".format(round(np.average(data5),2),round(np.std(data5),2),round(np.min(data5),2)))
    if len(data10) >0 :
        print("{0} {1} {2}".format(round(np.average(data10),2),round(np.std(data10),2),round(np.min(data10),2)))
        
   

    print("1年化:  平均 {0}\t標準差 {1}\t最小值 {2}".format(round(np.average(data),2),round(np.std(data),2),round(np.min(data),2)))
    if len(data3) >0 :
        print("3年化:  平均 {0}\t標準差 {1}\t最小值 {2}".format(round(np.average(data3),2),round(np.std(data3),2),round(np.min(data3),2)))
    if len(data4) >0 :
        print("4年化:  平均 {0}\t標準差 {1}\t最小值 {2}".format(round(np.average(data4),2),round(np.std(data4),2),round(np.min(data4),2)))
    if len(data5) >0 :
        print("5年化:  平均 {0}\t標準差 {1}\t最小值 {2}".format(round(np.average(data5),2),round(np.std(data5),2),round(np.min(data5),2)))
    if len(data10) >0 :
        print("10年化: 平均 {0}\t標準差 {1}\t最小值 {2}".format(round(np.average(data10),2),round(np.std(data10),2),round(np.min(data10),2)))
        
        
    #plt.plot_date( date, data , "-", label="1")
    #plt.plot_date( date3, data3 , "-", label="3")
    #plt.plot_date( date5, data5 , "-", label="5")
    #plt.grid()
    #plt.legend()
    #plt.show()
    
    #plt.plot_date( s.date, s.close, "-")
    #plt.grid()
    #plt.show()
    
    pulldown_date, pulldown = s.feature_pulldown(130) # 半年
    print("半年高檔拉回標準：", round(np.median(pulldown),3), "目前：", round(pulldown[-1],3))
    
    #5日 K
    s = stock_5day("測試資料/基金/{0}.csv".format(sys.argv[1]))
    list_K = s.feature_K()
    currnt_K = list_K[-1]
    plt.plot( list_K, "-")
    plt.grid()
    plt.show()
    
    plt.hist(list_K, 100)
    plt.grid()
    plt.show()
    list_K = np.sort(list_K)
    l = len(list_K)
    print("\r\nK 高低檔數值：", round(list_K[int(l*0.25)],2), round(list_K[int(l*0.75)],2), "目前 K：", round(currnt_K, 2))
    