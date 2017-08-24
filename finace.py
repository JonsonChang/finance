# -*- coding: utf-8 -*-  
import csv  
import numpy as np

MA = 47; #均線天數
BIAS_up_mean = 0  #乖離率的平均
BIAS_down_mean = 0  #乖離率的平均
BIAS_up_std = 0  #乖離率的標準差
BIAS_down_std = 0  #乖離率的標準差

UP_more = 0         #漲多
UP_too_more = 0     #漲太多
DOWN_more = 0       #跌多
DOWN_too_more = 0   #跌太多
 
f = open('table.csv', 'r')  
raw_data = [] 


def gat_MA(start_index):
    data = []
    try:
        for row in range(start_index,start_index+MA):
    #        print raw_data[row]
            data.append(float(raw_data[row][6]))  #Adj Close
        a = np.array(data)
        return np.mean(a, axis=0)
    except:
        return 0

def get_BIAS_mean_std():
    data_up = []
    data_down = []
    for row in raw_data:
        try:
            if (float(row[8]) > 0 ):
                data_up.append(float(row[8]))
            elif (float(row[8]) < 0 ):    
                data_down.append(float(row[8]))
        except:
            print
    up_array = np.array(data_up)
    down_array = np.array(data_down)
    
    
    
    a_BIAS_up_mean =  np.mean(up_array, axis=0)
    a_BIAS_up_std =  np.std(up_array, axis=0)
    a_BIAS_down_mean =  np.mean(down_array, axis=0)
    a_BIAS_down_std =  np.std(down_array, axis=0)
    
    return a_BIAS_up_mean, a_BIAS_up_std, a_BIAS_down_mean, a_BIAS_down_std

    
i = 0


for row in  csv.reader(f):
#將資料讀入 raw_data list 中
    raw_data.append(row)
f.close()  


#計算均線
i = 0
for row in raw_data:
    if i > 0 :
        row.append(gat_MA(i))
    i = i + 1

    
#計算乖離率
i = 0
for row in raw_data:
    if i > 0 :
        if(row[7] != 0):
            BIAS = (float(row[6]) - row[7]) / row[7]
        else:
            BIAS = 0
        row.append(BIAS)
    i = i + 1

#乖離率範圍，使用標準差
BIAS_up_mean, BIAS_up_std, BIAS_down_mean, BIAS_down_std  = get_BIAS_mean_std()  

print BIAS_up_mean
print BIAS_up_std
print BIAS_down_mean
print BIAS_down_std 

#漲多，跌多 1.5倍標準差
#漲太多，跌太多 2.5倍標準差
UP_more       = BIAS_up_mean+1.5*BIAS_up_std           #漲多
UP_too_more   = BIAS_up_mean+2.5*BIAS_up_std           #漲太多
DOWN_more     = BIAS_down_mean-1.5*BIAS_down_std       #跌多
DOWN_too_more = BIAS_down_mean-2.5*BIAS_down_std       #跌太多


#計算方向，偏多，偏空
i = 0
for row in raw_data:
    if i > 0 :
        try:
            cur_MA = raw_data[i][7]
            pre_MA = raw_data[i+1][7]
            if(pre_MA != 0):
                row.append(cur_MA - pre_MA)
            else:
                row.append(0)
        except:
            row.append(0)
    i = i + 1    
    
    
    
print "==debug dump=="
for row in raw_data:
    tmp = [];
    try:
        if (row[7] != 0):
            tmp.append(row[0])
            tmp.extend(row[6:])
            print  tmp
    except:
        print

print "==debug dump=="    
a = raw_data
print a[0]
print a[1]
print a[2]
print a[3]
print a[4]
print a[5]

print "漲多:{0} 漲太多：{1}，跌多：{2}  跌太多：{3}".format(UP_more,UP_too_more ,DOWN_more,DOWN_too_more)


#輸出


fa = open("output.csv","w")  
w = csv.writer(fa)  
#w.writerows(reversed(raw_data))  #反轉：越早越前面
w.writerows((raw_data))  
fa.close()  

