# -*- coding: utf-8 -*-
import numpy as np
import json
import csv
import time
from stock import stock
from datetime import datetime
import matplotlib.dates as mdates
import urllib.request, json 
import xlrd
import config_fund

Configs = config_fund.Configs

def get_datetime_cnyes_date(tradeDate):
    excel_date = (tradeDate/86400) + 25569.333333333333 # to excel date
    a = xlrd.xldate_as_tuple(excel_date,0)
    day_str = "{0}-{1}-{2}".format(a[0],a[1],a[2])
    #print(day_str)
    dt = datetime.strptime(day_str,'%Y-%m-%d')
    return dt

for config in Configs:
    print ("\r\n == ",config)
    
    s = stock(config['file_path'])
    last_date = s.date[-1]
    #print(last_date)
    

#配息
    URL = "http://fund.cnyes.com/api/v1/fund/{0}/dividend?page=".format(config['cnyes_id'])
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
            
    
#取得最新的資料    
    URL = "http://fund.cnyes.com/api/v1/fund/{0}/nav?format=table&page=".format(config['cnyes_id'])
    with urllib.request.urlopen("{0}1".format(URL)) as url:
        data = json.loads(url.read().decode())
    last_page = data['items']['last_page']

    out = np.array([0, 0])
    
    is_enough = False
    for page in range(1,last_page+1):
    #for page in range(1,2):
        print (page, "/", last_page)
        print ("{0}{1}".format(URL,page))
        #time.sleep(1)
        with urllib.request.urlopen("{0}{1}".format(URL,page)) as url:
            data = json.loads(url.read().decode())
            
        rawdata = data['items']['data']
        for item in rawdata:
            tradeDate = int(item['tradeDate'])
            nav = float(item['nav'])
            nav = true_val((tradeDate/86400) + 25569.333333333333,nav)
            tradeDate = get_datetime_cnyes_date(tradeDate)
            print(tradeDate, item['nav'])
            l = [tradeDate, nav]
            out = np.vstack([out, l])
            
            if(last_date > mdates.date2num(tradeDate)):
                print("OK: ",last_date, tradeDate )
                is_enough = True
                break
        if is_enough :
            break;
            
    out = out[1:]
    out = out[::-1]

    # 確認是否有需要更新資料        
    for new_data in out:
        #print(new_data[0],new_data[1], last_date)
        d = new_data[0]
        c = new_data[1]
        if(mdates.date2num(d) > last_date):
            str = "{0},{1},{2},{3},{4}".format(d.strftime('%Y/%m/%d'),"","","",c )
            print("資料回補：" + str)
            f = open(config['file_path'], 'a+')
            f.write(str+"\n")
            f.close()


