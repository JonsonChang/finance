# -*- coding: utf-8 -*-
import numpy as np
import json
import csv
import sys
import time
from datetime import datetime
import matplotlib.dates as mdates
import urllib.request, json 

ID = "B03,012"  #有配息
ID = "MSCN"  #有配息

#配息
URL = "http://fund.cnyes.com/api/v1/fund/{0}/dividend?page=".format(ID)
with urllib.request.urlopen("{0}1".format(URL)) as url:
    data = json.loads(url.read().decode())
last_page = data['items']['last_page']

dividend_date = []
dividend_val = []
for page in range(1,last_page+1):
    print (page, "/", last_page)
    with urllib.request.urlopen("{0}{1}".format(URL,page)) as url:
        data = json.loads(url.read().decode())
        
    rawdata = data['items']['data']
    for item in rawdata:
        tradeDate = int(item['excludingDate'])
        tradeDate = (tradeDate/86400) + 25569.333333333333 # to excel date
        nav = float(item['totalDistribution'])
        print(tradeDate, nav)
        dividend_date.append(tradeDate)
        dividend_val.append(nav)

dividend_date = dividend_date[::-1]
dividend_val = np.cumsum(dividend_val[::-1], dtype=float)

def true_val(current_date, current_val):
    val = 0
    last = len(dividend_date)
    if last < 1:
        return current_val
    if current_date < dividend_date[0]:
        return current_val    
    if current_date >= dividend_date[last-1]:
        return current_val + dividend_val[last-1]
    
    for idx, val in enumerate(dividend_date):
        if dividend_date[idx]<=current_date and dividend_date[idx+1]>current_date :
            return current_val + dividend_val[idx]
    
        
#淨值
URL = "http://fund.cnyes.com/api/v1/fund/{0}/nav?format=table&page=".format(ID)

with urllib.request.urlopen("{0}1".format(URL)) as url:
    data = json.loads(url.read().decode())
last_page = data['items']['last_page']

out = np.array([0, 0])

for page in range(1,last_page+1):
#for page in range(1,3):
    repeat = True
    while repeat:
        try:
            print (page, "/", last_page)
            #time.sleep(1)
            with urllib.request.urlopen("{0}{1}".format(URL,page)) as url:
                data = json.loads(url.read().decode())
                
            rawdata = data['items']['data']
            for item in rawdata:
                tradeDate = int(item['tradeDate'])
                tradeDate = (tradeDate/86400) + 25569.333333333333 # to excel date
                nav = float(item['nav'])
                nav = true_val(tradeDate, nav) #還原配息值
                print(tradeDate, item['nav'])
                l = [tradeDate, nav]
                out = np.vstack([out, l])
        except:
            print("Unexpected error:", sys.exc_info()[0])
            time.sleep(3)
            repeat = True
        else:
            repeat = False


out = out[1:]
np.savetxt("{0}.csv".format(ID), out[::-1], delimiter=",",header="d,c" )
