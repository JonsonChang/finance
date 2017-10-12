# -*- coding: utf-8 -*-
import numpy as np
import json
import csv
from datetime import datetime
import matplotlib.dates as mdates


def excel_date(date1):
    temp = datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
    delta = date1 - temp
    return float(delta.days) + (float(delta.seconds) / 86400)


with open('AA.txt', 'r') as f:
    array = json.load(f)

out = np.array([0, 0])
oldday = 0
for row in array:
    d = excel_date(datetime.strptime(row['TransDate'], '%Y%m%d'))
    l = [(d), row['Price']]
    if oldday != d:
        oldday = d  # 刪除重複的日期
        out = np.vstack([out, l])


np.savetxt("GG.csv", out, delimiter=",")
