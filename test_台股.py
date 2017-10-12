# -*- coding: utf-8 -*-
import numpy as np
import sys
from stock import stock
from stock import stock_5day
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.finance import candlestick_ohlc

            
if __name__ == '__main__':
    s = stock("測試資料/台股/{0}.csv".format(sys.argv[1]))
    nday = int(sys.argv[2]) #設定主軸
    period = 12
    date, data = s.feature_Annualized(1, period)
    date2, data2 = s.feature_Annualized(2, period)
    date3, data3 = s.feature_Annualized(3, period)
    date4, data4 = s.feature_Annualized(4, period)
    date5, data5 = s.feature_Annualized(5, period)
    date6, data6 = s.feature_Annualized(6, period)
    date7, data7 = s.feature_Annualized(7, period)
    date8, data8 = s.feature_Annualized(8, period)
    date9, data9 = s.feature_Annualized(9, period)
    date10, data10 = s.feature_Annualized(10, period)
    
    #print("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14}".format(
    #    round(np.average(data),2),round(np.std(data),2),round(np.min(data),2),
    #    round(np.average(data3),2),round(np.std(data3),2),round(np.min(data3),2),
    #    round(np.average(data4),2),round(np.std(data4),2),round(np.min(data4),2),
    #    round(np.average(data5),2),round(np.std(data5),2),round(np.min(data5),2),
    #    round(np.average(data10),2),round(np.std(data10),2),round(np.min(data10),2)
    #    ))
    #    
    print("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14} {15} {16} {17} {18} {19} {20} {21} {22} {23} {24} {25} {26} {27} {28} {29}".format(
        round(np.average(data),2),round(np.std(data),2),round(np.min(data),2),
        round(np.average(data2),2),round(np.std(data2),2),round(np.min(data2),2),
        round(np.average(data3),2),round(np.std(data3),2),round(np.min(data3),2),
        round(np.average(data4),2),round(np.std(data4),2),round(np.min(data4),2),
        round(np.average(data5),2),round(np.std(data5),2),round(np.min(data5),2),
        round(np.average(data6),2),round(np.std(data6),2),round(np.min(data6),2),
        round(np.average(data7),2),round(np.std(data7),2),round(np.min(data7),2),
        round(np.average(data8),2),round(np.std(data8),2),round(np.min(data8),2),
        round(np.average(data9),2),round(np.std(data9),2),round(np.min(data9),2),
        round(np.average(data10),2),round(np.std(data10),2),round(np.min(data10),2)
        ))        
   

    print("1年化:  平均 {0}\t標準差 {1}\t最小值 {2}".format(round(np.average(data),2),round(np.std(data),2),round(np.min(data),2)))
    if len(data3) >0 :
        print("3年化:  平均 {0}\t標準差 {1}\t最小值 {2}".format(round(np.average(data3),2),round(np.std(data3),2),round(np.min(data3),2)))
    if len(data4) >0 :
        print("4年化:  平均 {0}\t標準差 {1}\t最小值 {2}".format(round(np.average(data4),2),round(np.std(data4),2),round(np.min(data4),2)))
    if len(data5) >0 :
        print("5年化:  平均 {0}\t標準差 {1}\t最小值 {2}".format(round(np.average(data5),2),round(np.std(data5),2),round(np.min(data5),2)))
    if len(data10) >0 :
        print("10年化: 平均 {0}\t標準差 {1}\t最小值 {2}".format(round(np.average(data10),2),round(np.std(data10),2),round(np.min(data10),2)))
        
        
    plt.plot_date( date, data , "-", label="1")
    plt.plot_date( date3, data3 , "-", label="3")
    plt.plot_date( date5, data5 , "-", label="5")
    plt.grid()
    plt.legend()
    #plt.show()

    print("*-*-*-*-*-*-*")
    
    s = stock("測試資料/台股/{0}d.csv".format(sys.argv[1]))
    pulldown_date, pulldown = s.feature_pulldown(20*6) # 半年
    print("半年高檔拉回標準：", round(np.median(pulldown),3), "目前：", round(pulldown[-1],3)) # 取中位數為標準
    
    BIAS = s.feature_BIAS(nday)
    BIAS_low = list(filter(lambda x: x < 0, BIAS[nday:]))
    print("主軸拉回標準：", round(np.median(BIAS_low)*100,3), "目前：", round(BIAS[-1]*100,3)) # 取中位數為標準
    
        
    #1日 K
    list_K = s.feature_K()
    currnt_K = list_K[-1]
    list_K = np.sort(list_K)
    l = len(list_K)

    print("1日K 高低檔數值：", round(list_K[int(l*0.20)],2), round(list_K[int(l*0.80)],2), "目前 K：", round(currnt_K, 2))    
    
    #5日 K
    s = stock_5day("測試資料/台股/{0}d.csv".format(sys.argv[1]))
    list_K = s.feature_K()
    currnt_K = list_K[-1]
    list_K = np.sort(list_K)
    l = len(list_K)
    print("5日K 高低檔數值：", round(list_K[int(l*0.20)],2), round(list_K[int(l*0.80)],2), "目前 K：", round(currnt_K, 2))

        
    
    
    