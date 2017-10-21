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