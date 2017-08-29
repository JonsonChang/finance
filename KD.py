# -*- coding: utf-8 -*-
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

def non_shuffling_train_test_split(X, y, test_size=0.2):
    i = int((1 - test_size) * X.shape[0]) + 1
    X_train, X_test = np.split(X, [i])
    y_train, y_test = np.split(y, [i])
    return X_train, X_test, y_train, y_test

stock_TPE = stock('price_data.csv')
all_days = len(stock_TPE.close)
K0 = np.array(stock_TPE.feature_K())
K1 = np.roll(K0, 1)
K2 = np.roll(K0, 2)
K3 = np.roll(K0, 3)
K4 = np.roll(K0, 4)
K5 = np.roll(K0, 5)
K6 = np.roll(K0, 6)
K7 = np.roll(K0, 7)
K8 = np.roll(K0, 8)
K9 = np.roll(K0, 9)

B5 = stock_TPE.feature_BIAS(5)
B10 = stock_TPE.feature_BIAS(10)
B15 = stock_TPE.feature_BIAS(15)


score = -99
score_list = []
for nday in range(1, 10):  # n天後的漲跌
#    for k_value in range(70,90):
        y = np.roll(stock_TPE.high, -nday) - np.array(stock_TPE.close)  #做多
#        y = np.roll(stock_TPE.high, -nday) - np.array(stock_TPE.feature_High(3))  #做多，超過前3天的最高值
        # y = np.array(stock_TPE.close) - np.roll(stock_TPE.low, -nday)  # 做空
    
        for index, data in enumerate(y):
            if(data > 0 ):
                y[index] = 1
            else:
                y[index] = 0
    
        x = np.stack(zip(B5))  # todo 需要多個feature
    
        # 去除不正確的data
        x = x[10:all_days - nday - 2]
        y = y[10:all_days - nday - 2]
    
        if(len(x) != len(y)):
            print('Error len(x) != len(y))')
            sys.exit()
    
#        X_train, X_test, y_train, y_test = train_test_split(
#            x, y, test_size=0.3)  # 同時做資料打亂
        X_train, X_test, y_train, y_test = non_shuffling_train_test_split(
            x, y, test_size=0.1)  # 不打亂資料
    
            
    
        #model = LinearRegression()
        model = KNeighborsClassifier()
        #model = DecisionTreeClassifier()

        model.fit(X_train, y_train)
        y_predict = model.predict(X_test)
        tmp_score = model.score(X_test, y_test)
        if(tmp_score > score):
            score = tmp_score
            score_list.append(score)
            print(nday,k_value, score)
#            np.savetxt("foo.csv", np.stack(zip(y_predict, y_test)), delimiter=",")
#            print("Classification report for classifier %s:\n%s\n"
#                % (model, metrics.classification_report(y_test, y_predict)))
#            print("Confusion matrix:\n%s"
#                % metrics.confusion_matrix(y_test, y_predict))
#    

# 畫圖
#from sklearn.cross_validation import cross_val_predict
#
#x = x[60:tmp_size]
#y = y[60:tmp_size]
#predicted = cross_val_predict(model, x, y, cv=10)
#fig, ax = plt.subplots()
#ax.scatter(y, predicted)
#ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
# ax.set_xlabel('Measured')
# ax.set_ylabel('Predicted')
# plt.show()
