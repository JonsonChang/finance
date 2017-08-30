# -*- coding: utf-8 -*-
# 常態分佈測試

import sys
import matplotlib.pyplot as plt
import numpy as np

from sklearn import datasets, svm, metrics
from sklearn.model_selection import train_test_split
from stock import stock
import matplotlib.pyplot as plt

# learning model
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

s = stock("price_data.csv")
nday = 45

good_mean = -100
for nday in range(1,100):
    data = np.array(s.close)
    data = (np.roll(data,-nday) - data)/data
    data = data[nday:len(data)-nday -1]
    
    
    num_bins = 50     
#    n, bins, patches = plt.hist(data, num_bins, normed=1, facecolor='blue', alpha=0.5) 
    if(data.mean()*100 > good_mean):
        good_mean = data.mean()*100
        print(nday, data.mean()*100, data.std()*100)


#    result = []
#    for i in range(0,len(data),nday):
#        result.append(data[i])        
#    n, bins, patches = plt.hist(result, num_bins, normed=1, facecolor='red', alpha=0.5) 
#    result = np.array(result)
#    if(result.mean()*100 > good_mean):
#        good_mean = result.mean()*100
#        print(nday, result.mean()*100, result.std()*100)

#分別計算 上漲 和 下跌 的常態分佈
up_mean = -100
down_mean = -100


for nday in range(1,100):
    data = np.array(s.close)
    data = (np.roll(data,-nday) - data)/data
    data = data[nday:len(data)-nday -1]
    
    up =[]
    down =[]
    for up_or_down in data:
        if(up_or_down > 0):
            up.append(up_or_down)
        elif(up_or_down < 0):
            down.append(up_or_down)
    
    up = np.array(up)
    down = np.array(down)
    num_bins = 50     
    
    n, bins, patches = plt.hist(up, num_bins, normed=1, facecolor='red', alpha=0.5) 
    n, bins, patches = plt.hist(down, num_bins, normed=1, facecolor='green', alpha=0.5) 
    print(nday, up.mean()*100, down.mean()*100)
