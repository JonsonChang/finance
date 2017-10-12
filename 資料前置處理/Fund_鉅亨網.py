# -*- coding: utf-8 -*-
import numpy as np
import json
import csv
import time
from datetime import datetime
import matplotlib.dates as mdates
import urllib.request, json 

ID = "B19,067"
URL = "http://fund.cnyes.com/api/v1/fund/{0}/nav?format=table&page=".format(ID)

with urllib.request.urlopen("{0}1".format(URL)) as url:
    data = json.loads(url.read().decode())
last_page = data['items']['last_page']

out = np.array([0, 0])
for page in range(1,last_page+1):
#for page in range(1,3):
    print (page, "/", last_page)
    #time.sleep(1)
    with urllib.request.urlopen("{0}{1}".format(URL,page)) as url:
        data = json.loads(url.read().decode())
        
    rawdata = data['items']['data']
    for item in rawdata:
        tradeDate = int(item['tradeDate'])
        tradeDate = (tradeDate/86400) + 25569.333333333333 # to excel date
        nav = float(item['nav'])
        print(tradeDate, item['nav'])
        l = [tradeDate, nav]
        out = np.vstack([out, l])
        
np.savetxt("{0}.csv".format(ID), out, delimiter=",")