# -*- coding: utf-8 -*-
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates


# normfun常態分佈函數，mu: 均值，sigma:標準差，pdf:機率密度函數，np.exp():機率密度函數公式
def normfun(x, mu, sigma):
    pdf = np.exp(-((x - mu)**2) / (2 * sigma**2)) / \
        (sigma * np.sqrt(2 * np.pi))
    return pdf

def normfun_ex(data):
    print("normfun_ex", data.mean(), data.std())
    x = np.arange(min(data), max(data), ((max(data) - min(data)) / 500))
    return x, normfun(x, data.mean(), data.std())

def time_filter(list_data, list_datetime, starttime=8*60, endtime=14*60):
    #跟據時間過濾資料
    result = []
    for index, data in enumerate(list_data):
        d = mdates.num2date(list_datetime[index])
        current = d.hour*60+d.minute
        if( current > starttime and current < endtime) :
            result.append(data)
    return np.array(result)

def num2time( n ):
    d = mdates.num2date(n)
    current = d.hour*60+d.minute
    return current
    
def list_percentage(arr, p): #回傳 list 中排序的百分比位罝的值。ex: 0.5 就是中位數 
    ll = np.sort(arr)
    l = len(ll)
    return (ll[int(l*p)])
    

def list_best_range(date, list, max = 0.8, min=0.2, n = 100 ) : #排序後定出上下限範圍
    up_list = []
    down_list = []
     
    for i in range(0, len(list)):
        start = i - n + 1
        end = i + 1
        if(start < 0):
            start = 0
        up_list.append(list_percentage(list[start:end],max))
        down_list.append(list_percentage(list[start:end],min))

    return date[n:], up_list[n:], down_list[n:]

def list_best_range_std(date, list, std_range=1.25 , n = 100) : #用標準差定出上下限範圍
    up_list = []
    down_list = []
     
    for i in range(0, len(list)):
        start = i - n + 1
        end = i + 1
        if(start < 0):
            start = 0
        
        avg = np.mean(list[start:end])
        std = np.std(list[start:end])
        up_list.append(avg + std_range*std)
        down_list.append(avg - std_range*std)
    return date[n:], up_list[n:], down_list[n:]    