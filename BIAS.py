# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np

from sklearn import datasets, svm, metrics
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


my_data = np.genfromtxt('price_data.csv', delimiter=',', skip_header=1)
my_data = my_data[::-1]  # 反向

#l_date = []
l_open = []
l_high = []
l_low = []
l_close = []
#l_volume = []

f_UpDown = []  # 當日的漲跌量
# f_UpDownMax = [] #當日最大的漲跌量


def moving_average(a, n=5):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    # return ret[n - 1:] / n
    return ret[:] / n


def BIAS(a, n=5):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    ret = ret / n  # average
    ret = (a / ret)
    ret = (1 - ret) * 100
    return ret[:]


for index, data in enumerate(my_data):
    tmp_open = data[1]
    tmp_high = data[2]
    tmp_low = data[3]
    tmp_close = data[4]

    l_open.append(tmp_open)
    l_high.append(tmp_high)
    l_low.append(tmp_low)
    l_close.append(tmp_close)

    f_UpDown.append(tmp_close - tmp_open)


f_ma5 = moving_average(l_close, n=5)
f_ma10 = moving_average(l_close, n=10)
#f_ma20 = moving_average(l_close, n=20)
#f_ma25 = moving_average(l_close, n=25)
#f_ma30 = moving_average(l_close, n=30)
#f_ma35 = moving_average(l_close, n=35)
#f_ma40 = moving_average(l_close, n=40)
#f_ma45 = moving_average(l_close, n=45)
f_BIAS5 = BIAS(l_close, n=5)
f_BIAS10 = BIAS(l_close, n=10)
f_BIAS20 = BIAS(l_close, n=20)
f_BIAS30 = BIAS(l_close, n=30)
f_BIAS40 = BIAS(l_close, n=40)
f_BIAS50 = BIAS(l_close, n=50)
f_BIAS60 = BIAS(l_close, n=60)

score = -99
for nday in range(1, 60):  # n天後的漲跌
    for l in range(1, 60):
        feature = BIAS(l_close, l)
        y = np.array(l_close)  # np.array 才能直接運算
        y[:-nday] = y[nday:] - y[:-nday]
        x = np.stack(zip(feature))  # todo 需要多個feature

        model = LinearRegression()
        tmp_size = len(x) - 100 - nday
        model.fit(x[60:tmp_size], y[60:tmp_size])
        y1 = model.predict(x[tmp_size:])
        tmp_score = model.score(x[tmp_size:], y[tmp_size:])
        if(tmp_score > score):
            score = tmp_score
            print(nday, l, score)


# 畫圖
from sklearn.cross_validation import cross_val_predict

x = x[60:tmp_size]
y = y[60:tmp_size]
predicted = cross_val_predict(model, x, y, cv=10)
fig, ax = plt.subplots()
ax.scatter(y, predicted)
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
ax.set_xlabel('Measured')
ax.set_ylabel('Predicted')
plt.show()

