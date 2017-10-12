# -*- coding: utf-8 -*-
import numpy as np
import json
import csv
from datetime import datetime
import matplotlib.dates as mdates


out = []
f = open('D:\system_download\TxfTwse_1min\TXF1-分鐘-成交價.csv', 'r')
for row in csv.reader(f):
    new_datetime = row[0] + " " + row[1]
    line = [new_datetime, row[2],row[3],row[4],row[5],row[6]]
    out.append(line)
f.close()

fout = open("stockaa.csv","w",newline='')
w = csv.writer(fout,delimiter=',')
w.writerows(out)
fout.close()
    
    
#with open('AA.txt', 'r') as f:
#    array = json.load(f)
#
#out = np.array([0, 0])
#oldday = 0
#for row in array:
#    d = excel_date(datetime.strptime(row['TransDate'], '%Y%m%d'))
#    l = [(d), row['Price']]
#    if oldday != d:
#        oldday = d  # 刪除重複的日期
#        out = np.vstack([out, l])
#
#
#np.savetxt("a.csv", out, delimiter=",")
