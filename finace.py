# -*- coding: utf-8 -*-  
import csv  
import numpy as np

MA = 47; #均線天數

f = open('table.csv', 'r')  
raw_data = [] 


def gat_MA(start_index):
    data = []
    for row in range(start_index,start_index+MA):
#        print raw_data[row]
        data.append(raw_data[row][6])  #Adj Close
    a = np.array(data)
    return a.mean

i = 0


for row in  csv.reader(f):
    raw_data.append(row)
f.close()  


a = raw_data
print a[0]
print a[1]
print a[2]

print gat_MA(1)



#計算均線

#計算乖離率

#計算標準差

