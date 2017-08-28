# -*- coding: utf-8 -*-
import numpy as np


class stock:
    def __init__(self, filename):
        self.raw = np.genfromtxt(
            filename,
            delimiter=',',
            skip_header=1)
        self.raw = self.raw[::-1]  # 反向

        self.opened = []
        self.high = []
        self.low = []
        self.close = []

        for index, data in enumerate(self.raw):
            tmp_open = data[1]
            tmp_high = data[2]
            tmp_low = data[3]
            tmp_close = data[4]
            self.opened.append(tmp_open)
            self.high.append(tmp_high)
            self.low.append(tmp_low)
            self.close.append(tmp_close)
            #f_UpDown.append(tmp_close - tmp_open)

    def feature_MA(self, n=5):  # 移動平均線
        ret = np.cumsum(self.close, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        # return ret[n - 1:] / n
        return ret[:] / n

    def feature_BIAS(self, n=5):  # 乖離率
        ret = np.cumsum(self.close, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        ret = ret / n  # average
        ret = (self.close / ret)
        ret = (1 - ret) * 100
        return ret[:]

    def feature_RSV(self, n=9):
        high_n = []
        low_n = []
        result = []
        for i in range(0, len(self.high)):
            start = i - n + 1
            end = i + 1
            if(start < 0):
                start = 0

            high_n.append(max(self.high[start:end]))
            low_n.append(min(self.low[start:end]))

        h = np.array(high_n)
        l = np.array(low_n)
        c = np.array(self.close)
        result = ((c - l) / (h - l)) * 100
        return (result)

    def feature_K(self, n=9):
        K = []
        RSV = self.feature_RSV(n)
        for i in range(0, len(self.high)):
            pre_K = 50
            if(i > 0):
                pre_K = K[i - 1]
            current_K = pre_K * (2 / 3) + RSV[i] * (1 / 3)
            K.append(current_K)
        return K

    def feature_D(self, n=9):
        D = []
        K = self.feature_K(n)
        for i in range(0, len(self.high)):
            pre_D = 50
            if(i > 0):
                pre_D = D[i - 1]
            current_D = pre_D * (2 / 3) + K[i] * (1 / 3)
            D.append(current_D)
        return D


#a = stock("price_data.csv")
#b = a.feature_K()
#rsv = a.feature_RSV()
