# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from numpy import genfromtxt

from sklearn import datasets, svm, metrics
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

my_data = genfromtxt('price_data.csv', delimiter=',', skip_header=1)
my_data = my_data[::-1]  # 反向

y = []
x = []

plt.plot(my_data)
plt.show()

#target1 未來一週會上漲5% and 中間跌少於3%，
#target 預測未來一週漲跌數

for index, data in enumerate(my_data):
    pass
    print(index, my_data.index(index))

iris = datasets.load_boston()
iris_X = iris.data
iris_y = iris.target

#X_train, X_test, y_train, y_test = train_test_split(iris_X, iris_y, test_size=0.3)
