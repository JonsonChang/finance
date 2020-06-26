# -*- coding: utf-8 -*-
import numpy as np
import sys
import os
import tools
from stock import stock
from stock import stock_5day
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#import commentjson  #使用pyinstall 會有file not found error
import json
from colorama import init, Fore, Back, Style
init(autoreset=True)

# Using an implicitly registered datetime converter for a matplotlib plotting method. The converter was registered by pandas on import. Future versions of pandas will require you to explicitly register matplotlib converters.
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

#讀取設定檔
f = open('config_stock.tw.json', "r",  encoding='UTF-8')
#Configs = commentjson.loads(f.read())
Configs = json.loads(f.read())
f.close()



def get_next_day_price(dara_list, idx):
    try:
        return(dara_list[idx+1])
    except  IndexError :
        return(dara_list[idx])
        


def buy_point_fixed_KD(ax, close, K_date, K):
    buy_date = []
    buy = []
    sell_date = []
    sell = []
    
    for i in range(2, len(K_date)):
        if K[i]<20 and K[i-1]>20:
            buy_date.append(K_date[i])
            buy.append(close[i]*0.99)
            
        if K[i]>80 and K[i-1]<80:
            sell_date.append(K_date[i])
            sell.append(close[i]*1.01)            
    ax.plot_date(buy_date, buy,"r^")
    ax.plot_date(sell_date, sell,"gv")


def get_val_by_date(d_list, val_list, d):
    if len(d_list) != len(val_list) :
        return 99999
    
    # 可修改看比例，快速找出大概的位置
    for idx, current_date in enumerate(d_list):
        if d == current_date:
            return val_list[idx]
    return 9999


def trade_model_guava_v3(start_date_str, ax, stock_obj, K_date, K, K_UD_date, K_up, K_down): 
    print("==v3==")
    #每次加碼時，都比買進目前的張數的2倍
    #賣出時，依次數平均賣出，ex: 進場5次，共持有20張，每次賣4張，分5次賣
    
    close = stock_obj.close
    h = stock_obj.high
    l = stock_obj.low
    
    K_up_date_list = []
    K_up_val_list = []
    K_down_date_list = []
    K_down_val_list = []
    
    average_cost = 0 # 平均成本
    share_count  = 0  #持有張數
    entry_count = 0 #進場次數
    exit_count = 0 #出場次數
    buy_sum = 0 # 買入總金額
    sell_sum = 0 # 賣出總金額
    unrealized_profit = 0 # 未實現損益 
    realized_profit = 0 # 已實現損益 
    profit_stop_counter = 0 # 計算第幾次出場
    
    percentage = 0.1  # 10% = 0.1, 
    
    start_date =mdates.date2num(datetime.strptime(start_date_str,'%Y/%m/%d'))
    
    
    for idx, current_date in enumerate(K_date):
        if current_date > start_date:
            up = get_val_by_date(K_UD_date, K_up, current_date)
            down = get_val_by_date(K_UD_date, K_down, current_date)
            
            
            if K[idx]<down:
                K_down_date_list.append(current_date)
                K_down_val_list.append(close[idx]*0.99)
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 低檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            if K[idx]>up:
                K_up_date_list.append(current_date)
                K_up_val_list.append(close[idx]*1.01)             
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 高檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            #第一次買進
            if share_count == 0 and K[idx]<down:
                average_cost = close[idx]
                entry_count = 1
                share_count = 1
                buy_sum = close[idx]
                print ("{0} {color}買進{color_reset} 目前張數:{1:.2f}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f}, 第一次出場:{5:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),average_cost*(1+percentage),close[idx], color=Fore.RED,color_reset=Fore.RESET))
                
            #加碼買進，出現訊號，且虧損10%
            if share_count >0 and K[idx]<down and close[idx] < average_cost*(1-percentage):
                entry_count = entry_count +1
                add_shares = share_count*2
                #print("加買張數 {}".format(add_shares))
                average_cost = (average_cost * share_count + close[idx]*add_shares)/(share_count + add_shares)
                share_count = share_count + add_shares
                buy_sum = buy_sum + close[idx]*add_shares
                if profit_stop_counter > 0:
                    profit_stop_counter = profit_stop_counter-1
                print ("{0} {color}買進{color_reset} 目前張數:{1:.2f}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f}, 第一次出場:{5:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),average_cost*(1+percentage),close[idx], color=Fore.RED,color_reset=Fore.RESET))
                
                #realized_profit = realized_profit + close[idx]-average_cost
                unrealized_profit = (close[idx] -average_cost)*share_count
                all_profit = (realized_profit+unrealized_profit)/buy_sum
                print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {color}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100, color=Fore.CYAN,color_reset=Fore.RESET))
            
            #賣出
            if share_count >0 and K[idx] > up:
                #計算停利點
                profit_stop = 9999
                if exit_count == 0 or profit_stop_counter == 0:
                    profit_stop_multiple =  (1+percentage)
                    profit_stop_counter = 0
                else:
                    profit_stop_multiple =  1+ (profit_stop_counter+1)*percentage
                profit_stop = profit_stop_multiple * average_cost
                #print(profit_stop , profit_stop_multiple , average_cost )
                if h[idx] > profit_stop:
                    profit_stop_counter = profit_stop_counter +1 
                    exit_count = exit_count +1 
                    del_shares = share_count/(entry_count - (exit_count-1))
                    
                    #print("\n入場次數 {} 出場次數 {} ,賣出股數{}  分成{}".format(entry_count, exit_count,del_shares,(entry_count - (exit_count-1))))
                    
                    share_count = share_count -del_shares
                    sell_sum = sell_sum + close[idx]*del_shares
                    print ("{0} {color}賣出{color_reset} 目前張數:{1:.2f}, 倍數：{8:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f} 停利標準: {5:.2f}, 最高價:{6:.2f} 收盤價:{7:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*0.9,profit_stop, h[idx],close[idx],profit_stop_multiple,color=Fore.GREEN,color_reset=Fore.RESET))
                    
                    realized_profit = realized_profit + (close[idx]-average_cost)*del_shares
                    unrealized_profit = (close[idx] -average_cost)*share_count
                    all_profit = (realized_profit+unrealized_profit)/buy_sum
                    print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {color}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100, color=Fore.CYAN,color_reset=Fore.RESET))
                
                if share_count == 0:
                    average_cost = 0 # 平均成本
                    share_count  = 0  #持有張數
                    entry_count = 0 #進場次數
                    exit_count = 0 #出場次數
                    buy_sum = 0 # 買入總金額
                    sell_sum = 0 # 賣出總金額
                    unrealized_profit = 0 # 未實現損益 
                    realized_profit = 0 # 已實現損益 
                    print("")
    
    ax.plot_date(K_up_date_list, K_up_val_list,"rv")
    ax.plot_date(K_down_date_list, K_down_val_list,"g^")
    
#目前狀況
    
    date_str = mdates.num2date(stock_obj.date[-1]).strftime("%Y/%m/%d")
    if share_count > 0 :
        unrealized_profit = (close[-1] -average_cost)*share_count
        all_profit = (realized_profit+unrealized_profit)/buy_sum
        print("\r\n")
        print ("{5}\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {6}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100,date_str, Fore.WHITE + Style.BRIGHT))
    print("{0}\t目前 K:{1:.2f}, 合理低檔:{2:.2f},合理高檔:{3:.2f}, 收盤價:{4:.2f}".format(date_str, K[-1], down,up, close[-1]))
    if K[-1] < down :
        print("\t",Fore.YELLOW + Back.GREEN + Style.BRIGHT +"--- 低檔 ---")
    if K[-1] > up :    
        print("\t",Fore.YELLOW + Back.RED + Style.BRIGHT +"+++ 高檔 +++")    
    
#目前狀況
    if share_count > 0 :
        date_str = mdates.num2date(stock_obj.date[-1]).strftime("%Y/%m/%d")
        unrealized_profit = (close[-1] -average_cost)*share_count
        all_profit = (realized_profit+unrealized_profit)/buy_sum
        print ("{5}\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100,date_str))
           
    

def trade_model_guava_v2(start_date_str, ax, stock_obj, K_date, K, K_UD_date, K_up, K_down): 
    print("==v2==")
    #每次加碼時，都比買進目前的張數
    #賣出時，依次數平均賣出，ex: 進場5次，共持有20張，每次賣4張，分5次賣
    
    close = stock_obj.close
    h = stock_obj.high
    l = stock_obj.low
    
    K_up_date_list = []
    K_up_val_list = []
    K_down_date_list = []
    K_down_val_list = []
    
    average_cost = 0 # 平均成本
    share_count  = 0  #持有張數
    entry_count = 0 #進場次數
    exit_count = 0 #出場次數
    buy_sum = 0 # 買入總金額
    sell_sum = 0 # 賣出總金額
    unrealized_profit = 0 # 未實現損益 
    realized_profit = 0 # 已實現損益 
    profit_stop_counter = 0 # 計算第幾次出場
    
    percentage = 0.1  # 10% = 0.1, 
    
    start_date =mdates.date2num(datetime.strptime(start_date_str,'%Y/%m/%d'))
    
    
    for idx, current_date in enumerate(K_date):
        if current_date > start_date:
            up = get_val_by_date(K_UD_date, K_up, current_date)
            down = get_val_by_date(K_UD_date, K_down, current_date)
            
            
            if K[idx]<down:
                K_down_date_list.append(current_date)
                K_down_val_list.append(close[idx]*0.99)
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 低檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            if K[idx]>up:
                K_up_date_list.append(current_date)
                K_up_val_list.append(close[idx]*1.01)             
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 高檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            #第一次買進
            if share_count == 0 and K[idx]<down:
                average_cost = close[idx]
                entry_count = 1
                share_count = 1
                buy_sum = close[idx]
                print ("{0} {color}買進{color_reset} 目前張數:{1:.2f}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f}, 第一次出場:{5:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),average_cost*(1+percentage),close[idx], color=Fore.RED,color_reset=Fore.RESET))
                
            #加碼買進，出現訊號，且虧損10%
            if share_count >0 and K[idx]<down and close[idx] < average_cost*(1-percentage):
                entry_count = entry_count +1
                add_shares = share_count
                #print("加買張數 {}".format(add_shares))
                average_cost = (average_cost * share_count + close[idx]*add_shares)/(share_count + add_shares)
                share_count = share_count + add_shares
                buy_sum = buy_sum + close[idx]*add_shares
                if profit_stop_counter > 0:
                    profit_stop_counter = profit_stop_counter-1
                print ("{0} {color}買進{color_reset} 目前張數:{1:.2f}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f}, 第一次出場:{5:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),average_cost*(1+percentage),close[idx], color=Fore.RED,color_reset=Fore.RESET))
                
                #realized_profit = realized_profit + close[idx]-average_cost
                unrealized_profit = (close[idx] -average_cost)*share_count
                all_profit = (realized_profit+unrealized_profit)/buy_sum
                print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {color}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100, color=Fore.CYAN,color_reset=Fore.RESET))
            
            #賣出
            if share_count >0 and K[idx] > up:
                #計算停利點
                profit_stop = 9999
                if exit_count == 0 or profit_stop_counter == 0:
                    profit_stop_multiple =  (1+percentage)
                    profit_stop_counter = 0
                else:
                    profit_stop_multiple =  1+ (profit_stop_counter+1)*percentage
                profit_stop = profit_stop_multiple * average_cost
                #print(profit_stop , profit_stop_multiple , average_cost )
                if h[idx] > profit_stop:
                    profit_stop_counter = profit_stop_counter +1 
                    exit_count = exit_count +1 
                    del_shares = share_count/(entry_count - (exit_count-1))
                    
                    #print("\n入場次數 {} 出場次數 {} ,賣出股數{}  分成{}".format(entry_count, exit_count,del_shares,(entry_count - (exit_count-1))))
                    
                    share_count = share_count -del_shares
                    sell_sum = sell_sum + close[idx]*del_shares
                    print ("{0} {color}賣出{color_reset} 目前張數:{1:.2f}, 倍數：{8:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f} 停利標準: {5:.2f}, 最高價:{6:.2f} 收盤價:{7:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*0.9,profit_stop, h[idx],close[idx],profit_stop_multiple,color=Fore.GREEN,color_reset=Fore.RESET))
                    
                    realized_profit = realized_profit + (close[idx]-average_cost)*del_shares
                    unrealized_profit = (close[idx] -average_cost)*share_count
                    all_profit = (realized_profit+unrealized_profit)/buy_sum
                    print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {color}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100, color=Fore.CYAN,color_reset=Fore.RESET))
                
                if share_count == 0:
                    average_cost = 0 # 平均成本
                    share_count  = 0  #持有張數
                    entry_count = 0 #進場次數
                    exit_count = 0 #出場次數
                    buy_sum = 0 # 買入總金額
                    sell_sum = 0 # 賣出總金額
                    unrealized_profit = 0 # 未實現損益 
                    realized_profit = 0 # 已實現損益 
                    print("")
    
    ax.plot_date(K_up_date_list, K_up_val_list,"rv")
    ax.plot_date(K_down_date_list, K_down_val_list,"g^")
    
#目前狀況
    
    date_str = mdates.num2date(stock_obj.date[-1]).strftime("%Y/%m/%d")
    if share_count > 0 :
        unrealized_profit = (close[-1] -average_cost)*share_count
        all_profit = (realized_profit+unrealized_profit)/buy_sum
        print("\r\n")
        print ("{5}\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {6}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100,date_str, Fore.WHITE + Style.BRIGHT))
    print("{0}\t目前 K:{1:.2f}, 合理低檔:{2:.2f},合理高檔:{3:.2f}, 收盤價:{4:.2f}".format(date_str, K[-1], down,up, close[-1]))
    if K[-1] < down :
        print("\t",Fore.YELLOW + Back.GREEN + Style.BRIGHT +"--- 低檔 ---")
    if K[-1] > up :    
        print("\t",Fore.YELLOW + Back.RED + Style.BRIGHT +"+++ 高檔 +++")       

        
def trade_model_guava_v2_1(start_date_str, ax, stock_obj, K_date, K, K_UD_date, K_up, K_down): 
    print("==v2-1==")
    #進出場時機，K值反轉
    #每次加碼時，都比買進目前的張數
    #賣出時，依次數平均賣出，ex: 進場5次，共持有20張，每次賣4張，分5次賣
    
def trade_model_guava_v2_2(start_date_str, ax, stock_obj, K_date, K, K_UD_date, K_up, K_down,percent_date, percent_up, percent_down): 
    print("==v2-2==")
    #每次加碼時，都比買進目前的張數
    #賣出時，依次數平均賣出，ex: 進場5次，共持有20張，每次賣4張，分5次賣
    #動態計算 percentage ，最小值為 5%
    
    close = stock_obj.close
    h = stock_obj.high
    l = stock_obj.low
    
    K_up_date_list = []
    K_up_val_list = []
    K_down_date_list = []
    K_down_val_list = []
    
    average_cost = 0 # 平均成本
    share_count  = 0  #持有張數
    entry_count = 0 #進場次數
    exit_count = 0 #出場次數
    buy_sum = 0 # 買入總金額
    sell_sum = 0 # 賣出總金額
    unrealized_profit = 0 # 未實現損益 
    realized_profit = 0 # 已實現損益 
    profit_stop_counter = 0 # 計算第幾次出場
    
    percentage = 0.1  # 10% = 0.1, 
    
    start_date =mdates.date2num(datetime.strptime(start_date_str,'%Y/%m/%d'))
    
    
    for idx, current_date in enumerate(K_date):
        if current_date > start_date:
            up = get_val_by_date(K_UD_date, K_up, current_date)
            down = get_val_by_date(K_UD_date, K_down, current_date)
            
            
            if K[idx]<down:
                K_down_date_list.append(current_date)
                K_down_val_list.append(close[idx]*0.99)
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 低檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            if K[idx]>up:
                K_up_date_list.append(current_date)
                K_up_val_list.append(close[idx]*1.01)             
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 高檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            #第一次買進
            if share_count == 0 and K[idx]<down:
                average_cost = close[idx]
                entry_count = 1
                share_count = 1
                buy_sum = close[idx]
                print ("{0} {color}買進{color_reset} 目前張數:{1:.2f}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f}, 第一次出場:{5:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),average_cost*(1+percentage),close[idx], color=Fore.RED,color_reset=Fore.RESET))
                
            #加碼買進，出現訊號，且虧損10%
            percentage = get_val_by_date(percent_date, percent_down, current_date)
            if percentage < 0:
                percentage = -1 * percentage
            if percentage < 0.05:
                percentage = 0.05
            if share_count >0 and K[idx]<down and close[idx] < average_cost*(1-percentage):
                entry_count = entry_count +1
                add_shares = share_count
                #print("加買張數 {}".format(add_shares))
                average_cost = (average_cost * share_count + close[idx]*add_shares)/(share_count + add_shares)
                share_count = share_count + add_shares
                buy_sum = buy_sum + close[idx]*add_shares
                if profit_stop_counter > 0:
                    profit_stop_counter = profit_stop_counter-1
                print ("{0} {color}買進{color_reset} 目前張數:{1:.2f}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f}, 第一次出場:{5:.2f}, down percentage:{percentage:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),average_cost*(1+percentage),close[idx],percentage=percentage, color=Fore.RED,color_reset=Fore.RESET))
                
                #realized_profit = realized_profit + close[idx]-average_cost
                unrealized_profit = (close[idx] -average_cost)*share_count
                all_profit = (realized_profit+unrealized_profit)/buy_sum
                print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {color}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100, color=Fore.CYAN,color_reset=Fore.RESET))
            
            #賣出
            if share_count >0 and K[idx] > up:
                #計算停利百分比
                percentage = get_val_by_date(percent_date, percent_up, current_date)
                if percentage < 0:
                    percentage = -1 * percentage
                if percentage < 0.05:
                    percentage = 0.05                    
                    
                #計算停利點
                profit_stop = 9999
                if exit_count == 0 or profit_stop_counter == 0:
                    profit_stop_multiple =  (1+percentage)
                    profit_stop_counter = 0
                else:
                    profit_stop_multiple =  1+ (profit_stop_counter+1)*percentage
                profit_stop = profit_stop_multiple * average_cost
                #print(profit_stop , profit_stop_multiple , average_cost )
                if h[idx] > profit_stop:
                    profit_stop_counter = profit_stop_counter +1 
                    exit_count = exit_count +1 
                    del_shares = share_count/(entry_count - (exit_count-1))
                    
                    #print("\n入場次數 {} 出場次數 {} ,賣出股數{}  分成{}".format(entry_count, exit_count,del_shares,(entry_count - (exit_count-1))))
                    
                    share_count = share_count -del_shares
                    sell_sum = sell_sum + close[idx]*del_shares
                    print ("{0} {color}賣出{color_reset} 目前張數:{1:.2f}, 倍數：{8:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f} 停利標準: {5:.2f}, 最高價:{6:.2f} 收盤價:{7:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*0.9,profit_stop, h[idx],close[idx],profit_stop_multiple,color=Fore.GREEN,color_reset=Fore.RESET))
                    
                    realized_profit = realized_profit + (close[idx]-average_cost)*del_shares
                    unrealized_profit = (close[idx] -average_cost)*share_count
                    all_profit = (realized_profit+unrealized_profit)/buy_sum
                    print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {color}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100, color=Fore.CYAN,color_reset=Fore.RESET))
                
                if share_count == 0:
                    average_cost = 0 # 平均成本
                    share_count  = 0  #持有張數
                    entry_count = 0 #進場次數
                    exit_count = 0 #出場次數
                    buy_sum = 0 # 買入總金額
                    sell_sum = 0 # 賣出總金額
                    unrealized_profit = 0 # 未實現損益 
                    realized_profit = 0 # 已實現損益 
                    print("")
    
    ax.plot_date(K_up_date_list, K_up_val_list,"rv")
    ax.plot_date(K_down_date_list, K_down_val_list,"g^")
    
#目前狀況
    
    date_str = mdates.num2date(stock_obj.date[-1]).strftime("%Y/%m/%d")
    if share_count > 0 :
        unrealized_profit = (close[-1] -average_cost)*share_count
        all_profit = (realized_profit+unrealized_profit)/buy_sum
        print("\r\n")
        print ("{5}\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {6}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100,date_str, Fore.WHITE + Style.BRIGHT))
    print("{0}\t目前 K:{1:.2f}, 合理低檔:{2:.2f},合理高檔:{3:.2f}, 收盤價:{4:.2f}, 低：{5:.2f}% 高：{6:.2f}%".format(date_str, K[-1], down,up, close[-1], percent_down[-1]*100, percent_up[-1]*100))
    if K[-1] < down :
        print("\t",Fore.YELLOW + Back.GREEN + Style.BRIGHT +"--- 低檔 ---")
    if K[-1] > up :    
        print("\t",Fore.YELLOW + Back.RED + Style.BRIGHT +"+++ 高檔 +++")       


def trade_model_guava_v2_3(start_date_str, ax, stock_obj, K_date, K, K_UD_date, K_up, K_down,percent_date, percent_up, percent_down): 
    print("==v2-3==")
    #每次加碼時，都比買進目前的張數
    #賣出時，依次數平均賣出，ex: 進場5次，共持有20張，每次賣4張，分5次賣
    #動態計算 percentage ，最小值為 5%
    #進場超過2次時 down percentage 最小值為 10%. 
    
    close = stock_obj.close
    h = stock_obj.high
    l = stock_obj.low
    
    K_up_date_list = []
    K_up_val_list = []
    K_down_date_list = []
    K_down_val_list = []
    
    average_cost = 0 # 平均成本
    share_count  = 0  #持有張數
    entry_count = 0 #進場次數
    exit_count = 0 #出場次數
    buy_sum = 0 # 買入總金額
    sell_sum = 0 # 賣出總金額
    unrealized_profit = 0 # 未實現損益 
    realized_profit = 0 # 已實現損益 
    profit_stop_counter = 0 # 計算第幾次出場
    
    percentage = 0.1  # 10% = 0.1, 
    
    start_date =mdates.date2num(datetime.strptime(start_date_str,'%Y/%m/%d'))
    
    
    for idx, current_date in enumerate(K_date):
        if current_date > start_date:
            up = get_val_by_date(K_UD_date, K_up, current_date)
            down = get_val_by_date(K_UD_date, K_down, current_date)
            
            
            if K[idx]<down:
                K_down_date_list.append(current_date)
                K_down_val_list.append(close[idx]*0.99)
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 低檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            if K[idx]>up:
                K_up_date_list.append(current_date)
                K_up_val_list.append(close[idx]*1.01)             
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 高檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            #第一次買進
            if share_count == 0 and K[idx]<down:
                average_cost = close[idx]
                entry_count = 1
                share_count = 1
                buy_sum = close[idx]
                print ("{0} {color}買進{color_reset} 目前張數:{1:.2f}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f}, 第一次出場:{5:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),average_cost*(1+percentage),close[idx], color=Fore.RED,color_reset=Fore.RESET))
                
            #加碼買進，出現訊號，且虧損10%
            percentage = get_val_by_date(percent_date, percent_down, current_date)
            if percentage < 0:
                percentage = -1 * percentage
            if percentage < 0.05:
                percentage = 0.05
            if entry_count - exit_count >=2 and percentage < 0.1:
                percentage = 0.1
                
            if share_count >0 and K[idx]<down and close[idx] < average_cost*(1-percentage):
                entry_count = entry_count +1
                add_shares = share_count
                #print("加買張數 {}".format(add_shares))
                average_cost = (average_cost * share_count + close[idx]*add_shares)/(share_count + add_shares)
                share_count = share_count + add_shares
                buy_sum = buy_sum + close[idx]*add_shares
                if profit_stop_counter > 0:
                    profit_stop_counter = profit_stop_counter-1
                print ("{0} {color}買進{color_reset} 目前張數:{1:.2f}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f}, 第一次出場:{5:.2f}, down percentage:{percentage:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),average_cost*(1+percentage),close[idx],percentage=percentage, color=Fore.RED,color_reset=Fore.RESET))
                
                #realized_profit = realized_profit + close[idx]-average_cost
                unrealized_profit = (close[idx] -average_cost)*share_count
                all_profit = (realized_profit+unrealized_profit)/buy_sum
                print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {color}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100, color=Fore.CYAN,color_reset=Fore.RESET))
            
            #賣出
            if share_count >0 and K[idx] > up:
                #計算停利百分比
                percentage = get_val_by_date(percent_date, percent_up, current_date)
                if percentage < 0:
                    percentage = -1 * percentage
                if percentage < 0.05:
                    percentage = 0.05                    
                    
                #計算停利點
                profit_stop = 9999
                if exit_count == 0 or profit_stop_counter == 0:
                    profit_stop_multiple =  (1+percentage)
                    profit_stop_counter = 0
                else:
                    profit_stop_multiple =  1+ (profit_stop_counter+1)*percentage
                profit_stop = profit_stop_multiple * average_cost
                #print(profit_stop , profit_stop_multiple , average_cost )
                if h[idx] > profit_stop:
                    profit_stop_counter = profit_stop_counter +1 
                    exit_count = exit_count +1 
                    if (entry_count - (exit_count-1)) > 4:
                        tmp = entry_count - (exit_count-1) -4
                        exit_count = exit_count + tmp
                        del_shares = share_count/(entry_count - (exit_count-1))
                    else:
                        del_shares = share_count/(entry_count - (exit_count-1))
                    #del_shares = share_count/(entry_count - (exit_count-1))
                    
                    #print("\n入場次數 {} 出場次數 {} ,賣出股數{}  分成{}".format(entry_count, exit_count,del_shares,(entry_count - (exit_count-1))))
                    
                    share_count = share_count -del_shares
                    sell_sum = sell_sum + close[idx]*del_shares
                    print ("{0} {color}賣出{color_reset} 目前張數:{1:.2f}, 倍數：{8:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f} 停利標準: {5:.2f}, 最高價:{6:.2f} 收盤價:{7:.2f}, up percentage={percentage:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*0.9,profit_stop, h[idx],close[idx],profit_stop_multiple,percentage=percentage,color=Fore.GREEN,color_reset=Fore.RESET))
                    
                    realized_profit = realized_profit + (close[idx]-average_cost)*del_shares
                    unrealized_profit = (close[idx] -average_cost)*share_count
                    all_profit = (realized_profit+unrealized_profit)/buy_sum
                    print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {color}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100, color=Fore.CYAN,color_reset=Fore.RESET))
                
                if share_count == 0:
                    average_cost = 0 # 平均成本
                    share_count  = 0  #持有張數
                    entry_count = 0 #進場次數
                    exit_count = 0 #出場次數
                    buy_sum = 0 # 買入總金額
                    sell_sum = 0 # 賣出總金額
                    unrealized_profit = 0 # 未實現損益 
                    realized_profit = 0 # 已實現損益 
                    print("")
    
    ax.plot_date(K_up_date_list, K_up_val_list,"rv")
    ax.plot_date(K_down_date_list, K_down_val_list,"g^")
    
#目前狀況
    
    date_str = mdates.num2date(stock_obj.date[-1]).strftime("%Y/%m/%d")
    if share_count > 0 :
        unrealized_profit = (close[-1] -average_cost)*share_count
        all_profit = (realized_profit+unrealized_profit)/buy_sum
        print("\r\n")
        print ("{5}\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {6}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100,date_str, Fore.WHITE + Style.BRIGHT))
    print("{0}\t目前 K:{1:.2f}, 合理低檔:{2:.2f},合理高檔:{3:.2f}, 收盤價:{4:.2f}, 低：{5:.2f}% 高：{6:.2f}%".format(date_str, K[-1], down,up, close[-1], percent_down[-1]*100, percent_up[-1]*100))
    if K[-1] < down :
        print("\t",Fore.YELLOW + Back.GREEN + Style.BRIGHT +"--- 低檔 ---")
    if K[-1] > up :    
        print("\t",Fore.YELLOW + Back.RED + Style.BRIGHT +"+++ 高檔 +++")       

                       

def trade_model_guava_v2_4(start_date_str, ax, stock_obj, K_date, K, K_UD_date, K_up, K_down,percent_date, percent_up, percent_down): 
    print("== v2-4 ==")
    #每次加碼時，都比買進目前的張數
    #賣出時，依次數倒金字塔賣出
    #動態計算 percentage ，最小值為 5%
    #進場超過2次時 down percentage 最小值為 10%. 
    
    close = stock_obj.close
    h = stock_obj.high
    l = stock_obj.low
    
    K_up_date_list = []
    K_up_val_list = []
    K_down_date_list = []
    K_down_val_list = []
    
    average_cost = 0 # 平均成本
    share_count  = 0  #持有張數
    entry_count = 0 #進場次數
    exit_count = 0 #出場次數
    buy_sum = 0 # 買入總金額
    sell_sum = 0 # 賣出總金額
    unrealized_profit = 0 # 未實現損益 
    realized_profit = 0 # 已實現損益 
    profit_stop_counter = 0 # 計算第幾次出場
    profit_stop = 9999
    
    percentage = 0.1  # 10% = 0.1, 
    
    start_date =mdates.date2num(datetime.strptime(start_date_str,'%Y/%m/%d'))
    
    
    for idx, current_date in enumerate(K_date):
        if current_date > start_date:
            up = get_val_by_date(K_UD_date, K_up, current_date)
            down = get_val_by_date(K_UD_date, K_down, current_date)
            
            
            if K[idx]<down:
                K_down_date_list.append(current_date)
                K_down_val_list.append(close[idx]*0.99)
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 低檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            if K[idx]>up:
                K_up_date_list.append(current_date)
                K_up_val_list.append(close[idx]*1.01)             
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 高檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            #第一次買進
            if share_count == 0 and K[idx]<down:
                average_cost = close[idx]
                entry_count = 1
                share_count = 1
                buy_sum = close[idx]
                print ("{0} {color}買進{color_reset} 目前張數:{1:.2f}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f}, 下次出場:  , down% :{percentage:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),0,close[idx],percentage=percentage*100, color=Fore.RED,color_reset=Fore.RESET))
                
            #加碼買進，出現訊號，且虧損10%
            percentage = get_val_by_date(percent_date, percent_down, current_date)
            if percentage < 0:
                percentage = -1 * percentage
            if percentage < 0.05:
                percentage = 0.05
            if entry_count - exit_count >=2 and percentage < 0.1:
                percentage = 0.1
                
            if share_count >0 and K[idx]<down and close[idx] < average_cost*(1-percentage):
                entry_count = entry_count +1
                add_shares = share_count
                #print("加買張數 {}".format(add_shares))
                average_cost = (average_cost * share_count + close[idx]*add_shares)/(share_count + add_shares)
                share_count = share_count + add_shares
                buy_sum = buy_sum + close[idx]*add_shares
                if profit_stop_counter > 0:
                    profit_stop_counter = profit_stop_counter-1
                print ("{0} {color}買進{color_reset} 目前張數:{1:.2f}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f}, 下次出場:  , down% :{percentage:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),0,close[idx],percentage=percentage*100, color=Fore.RED,color_reset=Fore.RESET))
                
                #realized_profit = realized_profit + close[idx]-average_cost
                unrealized_profit = (close[idx] -average_cost)*share_count
                all_profit = (realized_profit+unrealized_profit)/buy_sum
                print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {color}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100, color=Fore.CYAN,color_reset=Fore.RESET))
            
        # *.*.*. 賣出 *.*.*.
            #計算停利百分比
            percentage = get_val_by_date(percent_date, percent_up, current_date)
            if percentage < 0:
                percentage = -1 * percentage
            if percentage < 0.05:
                percentage = 0.05                    
                
            #計算停利點
            profit_stop = 9999
            if exit_count == 0 or profit_stop_counter == 0:
                profit_stop_multiple =  (1+percentage)
                profit_stop_counter = 0
            else:
                profit_stop_multiple =  1+ (profit_stop_counter+1)*percentage
            profit_stop = profit_stop_multiple * average_cost
            #return profit_stop
            #print(profit_stop , profit_stop_multiple , average_cost )            

            
            if share_count >0 and K[idx] > up:
                if h[idx] > profit_stop:
                    profit_stop_counter = profit_stop_counter +1 
                    exit_count = exit_count +1 
                    if (entry_count - (exit_count-1)) > 4:
                        tmp = entry_count - (exit_count-1) -4
                        exit_count = exit_count + tmp
                        tmp = entry_count - (exit_count-1)
                        tmp = (tmp +1)*tmp/2
                        del_shares = share_count/tmp
                    else:
                        tmp = entry_count - (exit_count-1)
                        tmp = (tmp +1)*tmp/2
                        del_shares = share_count/tmp
                    #del_shares = share_count/(entry_count - (exit_count-1))
                    
                    #print("\n入場次數 {} 出場次數 {} ,賣出股數{}  分成{}".format(entry_count, exit_count,del_shares,(entry_count - (exit_count-1))))
                    
                    share_count = share_count -del_shares
                    sell_sum = sell_sum + close[idx]*del_shares
                    print ("{0} {color}賣出{color_reset} 目前張數:{1:.2f}, 賣出張數:{del_shares:.2f}(1/{tmp:.0f}), 倍數：{8:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f} 停利標準: {5:.2f}, 最高價:{6:.2f} 收盤價:{7:.2f}, up% ={percentage:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*0.9,profit_stop, h[idx],close[idx],profit_stop_multiple,del_shares=del_shares,percentage=percentage*100,color=Fore.GREEN,color_reset=Fore.RESET,tmp=tmp))
                    
                    realized_profit = realized_profit + (close[idx]-average_cost)*del_shares
                    unrealized_profit = (close[idx] -average_cost)*share_count
                    all_profit = (realized_profit+unrealized_profit)/buy_sum
                    print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {color}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100, color=Fore.CYAN,color_reset=Fore.RESET))
                
                if share_count == 0:
                    average_cost = 0 # 平均成本
                    share_count  = 0  #持有張數
                    entry_count = 0 #進場次數
                    exit_count = 0 #出場次數
                    buy_sum = 0 # 買入總金額
                    sell_sum = 0 # 賣出總金額
                    unrealized_profit = 0 # 未實現損益 
                    realized_profit = 0 # 已實現損益 
                    print("")
    
    ax.plot_date(K_up_date_list, K_up_val_list,"rv")
    ax.plot_date(K_down_date_list, K_down_val_list,"g^")
    
#目前狀況
    
    date_str = mdates.num2date(stock_obj.date[-1]).strftime("%Y/%m/%d")
    if share_count > 0 :
        unrealized_profit = (close[-1] -average_cost)*share_count
        all_profit = (realized_profit+unrealized_profit)/buy_sum
        print("\r\n")
        print ("{5}\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {6}{4:.2f}%, 下次出場：{profit_stop:.2f}".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100,date_str, Fore.WHITE + Style.BRIGHT,profit_stop=profit_stop))
    print("{0}\t目前 K:{1:.2f}, 合理低檔:{2:.2f},合理高檔:{3:.2f}, 收盤價:{4:.2f}, 低：{5:.2f}% 高：{6:.2f}%".format(date_str, K[-1], down,up, close[-1], percent_down[-1]*100, percent_up[-1]*100))
    if K[-1] < down :
        print("\t",Fore.YELLOW + Back.GREEN + Style.BRIGHT +"--- 低檔 ---")
    if K[-1] > up :    
        print("\t",Fore.YELLOW + Back.RED + Style.BRIGHT +"+++ 高檔 +++")       

        

def trade_model_guava_v2_5(start_date_str, ax, stock_obj, K_date, K, K_UD_date, K_up, K_down,percent_date, percent_up, percent_down): 
    print("== v2-5 ==")
    #每次加碼時，都比買進目前的張數
    #賣出時，依次數倒金字塔賣出
    #動態計算 percentage ，最小值為 5%
    #進場超過2次時 down percentage 最小值為 10%. 
    #第二天一開盤買進
    
    close = stock_obj.close
    o = stock_obj.opened
    h = stock_obj.high
    l = stock_obj.low
    
    K_up_date_list = []
    K_up_val_list = []
    K_down_date_list = []
    K_down_val_list = []
    
    average_cost = 0 # 平均成本
    share_count  = 0  #持有張數
    entry_count = 0 #進場次數
    exit_count = 0 #出場次數
    buy_sum = 0 # 買入總金額
    sell_sum = 0 # 賣出總金額
    unrealized_profit = 0 # 未實現損益 
    realized_profit = 0 # 已實現損益 
    profit_stop_counter = 0 # 計算第幾次出場
    profit_stop = 9999
    
    percentage = 0.1  # 10% = 0.1, 
    
    start_date =mdates.date2num(datetime.strptime(start_date_str,'%Y/%m/%d'))
    
    
    for idx, current_date in enumerate(K_date):
        if current_date > start_date:
            up = get_val_by_date(K_UD_date, K_up, current_date)
            down = get_val_by_date(K_UD_date, K_down, current_date)
            
            
            if K[idx]<down:
                K_down_date_list.append(current_date)
                K_down_val_list.append(close[idx]*0.99)
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 低檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            if K[idx]>up:
                K_up_date_list.append(current_date)
                K_up_val_list.append(close[idx]*1.01)             
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 高檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            #第一次買進
            if share_count == 0 and K[idx]<down:
                average_cost = get_next_day_price(o,idx)
                entry_count = 1
                share_count = 1
                buy_sum = get_next_day_price(o,idx)
                print ("{0} {color}買進{color_reset} 目前張數:{1:.2f}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f}, 下次出場:  , down% :{percentage:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),0,close[idx],percentage=percentage*100, color=Fore.RED,color_reset=Fore.RESET))
                
            #加碼買進，出現訊號，且虧損10%
            percentage = get_val_by_date(percent_date, percent_down, current_date)
            if percentage < 0:
                percentage = -1 * percentage
            if percentage < 0.05:
                percentage = 0.05
            if entry_count - exit_count >=2 and percentage < 0.1:
                percentage = 0.1
                
            if share_count >0 and K[idx]<down and close[idx] < average_cost*(1-percentage):
                entry_count = entry_count +1
                add_shares = share_count
                #print("加買張數 {}".format(add_shares))
                average_cost = (average_cost * share_count + get_next_day_price(o,idx)*add_shares)/(share_count + add_shares)
                share_count = share_count + add_shares
                buy_sum = buy_sum + get_next_day_price(o,idx)*add_shares
                if profit_stop_counter > 0:
                    profit_stop_counter = profit_stop_counter-1
                print ("{0} {color}買進{color_reset} 目前張數:{1:.2f}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f}, 下次出場:  , down% :{percentage:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),0,close[idx],percentage=percentage*100, color=Fore.RED,color_reset=Fore.RESET))
                
                #realized_profit = realized_profit + close[idx]-average_cost
                unrealized_profit = (close[idx] -average_cost)*share_count
                all_profit = (realized_profit+unrealized_profit)/buy_sum
                print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {color}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100, color=Fore.CYAN,color_reset=Fore.RESET))
            
        # *.*.*. 賣出 *.*.*.
            #計算停利百分比
            percentage = get_val_by_date(percent_date, percent_up, current_date)
            if percentage < 0:
                percentage = -1 * percentage
            if percentage < 0.05:
                percentage = 0.05                    
                
            #計算停利點
            profit_stop = 9999
            if exit_count == 0 or profit_stop_counter == 0:
                profit_stop_multiple =  (1+percentage)
                profit_stop_counter = 0
            else:
                profit_stop_multiple =  1+ (profit_stop_counter+1)*percentage
            profit_stop = profit_stop_multiple * average_cost
            #return profit_stop
            #print(profit_stop , profit_stop_multiple , average_cost )            

            
            if share_count >0 and K[idx] > up:
                if h[idx] > profit_stop:
                    profit_stop_counter = profit_stop_counter +1 
                    exit_count = exit_count +1 
                    if (entry_count - (exit_count-1)) > 4:
                        tmp = entry_count - (exit_count-1) -4
                        exit_count = exit_count + tmp
                        tmp = entry_count - (exit_count-1)
                        tmp = (tmp +1)*tmp/2
                        del_shares = share_count/tmp
                    else:
                        tmp = entry_count - (exit_count-1)
                        tmp = (tmp +1)*tmp/2
                        del_shares = share_count/tmp
                    #del_shares = share_count/(entry_count - (exit_count-1))
                    
                    #print("\n入場次數 {} 出場次數 {} ,賣出股數{}  分成{}".format(entry_count, exit_count,del_shares,(entry_count - (exit_count-1))))
                    
                    share_count = share_count -del_shares
                    sell_sum = sell_sum + close[idx]*del_shares
                    print ("{0} {color}賣出{color_reset} 目前張數:{1:.2f}, 賣出張數:{del_shares:.2f}(1/{tmp:.0f}), 倍數：{8:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f} 停利標準: {5:.2f}, 最高價:{6:.2f} 收盤價:{7:.2f}, up% ={percentage:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*0.9,profit_stop, h[idx],close[idx],profit_stop_multiple,del_shares=del_shares,percentage=percentage*100,color=Fore.GREEN,color_reset=Fore.RESET,tmp=tmp))
                    
                    realized_profit = realized_profit + (close[idx]-average_cost)*del_shares
                    unrealized_profit = (close[idx] -average_cost)*share_count
                    all_profit = (realized_profit+unrealized_profit)/buy_sum
                    print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {color}{4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100, color=Fore.CYAN,color_reset=Fore.RESET))
                
                if share_count == 0:
                    average_cost = 0 # 平均成本
                    share_count  = 0  #持有張數
                    entry_count = 0 #進場次數
                    exit_count = 0 #出場次數
                    buy_sum = 0 # 買入總金額
                    sell_sum = 0 # 賣出總金額
                    unrealized_profit = 0 # 未實現損益 
                    realized_profit = 0 # 已實現損益 
                    print("")
    
    ax.plot_date(K_up_date_list, K_up_val_list,"rv")
    ax.plot_date(K_down_date_list, K_down_val_list,"g^")
    
#目前狀況
    
    date_str = mdates.num2date(stock_obj.date[-1]).strftime("%Y/%m/%d")
    if share_count > 0 :
        unrealized_profit = (close[-1] -average_cost)*share_count
        all_profit = (realized_profit+unrealized_profit)/buy_sum
        print("\r\n")
        print ("{5}\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {6}{4:.2f}%, 下次出場：{profit_stop:.2f}".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100,date_str, Fore.WHITE + Style.BRIGHT,profit_stop=profit_stop))
    print("{0}\t目前 K:{1:.2f}, 合理低檔:{2:.2f},合理高檔:{3:.2f}, 收盤價:{4:.2f}, 低：{5:.2f}% 高：{6:.2f}%".format(date_str, K[-1], down,up, close[-1], percent_down[-1]*100, percent_up[-1]*100))
    if K[-1] < down :
        print("\t",Fore.YELLOW + Back.GREEN + Style.BRIGHT +"--- 低檔 ---")
    if K[-1] > up :    
        print("\t",Fore.YELLOW + Back.RED + Style.BRIGHT +"+++ 高檔 +++")       
        
        
                  
def trade_model_guava_v1(start_date_str, ax, stock_obj, K_date, K, K_UD_date, K_up, K_down): 
    print("==v1==")
    #每次加碼時，都比上一次多買一張
    #賣出時，依次數平均賣出，ex: 進場5次，共持有20張，每次賣4張，分5次賣
    
    close = stock_obj.close
    h = stock_obj.high
    l = stock_obj.low
    
    K_up_date_list = []
    K_up_val_list = []
    K_down_date_list = []
    K_down_val_list = []
    
    average_cost = 0 # 平均成本
    share_count  = 0  #持有張數
    entry_count = 0 #進場次數
    exit_count = 0 #出場次數
    buy_sum = 0 # 買入總金額
    sell_sum = 0 # 賣出總金額
    unrealized_profit = 0 # 未實現損益 
    realized_profit = 0 # 已實現損益 
    profit_stop_counter = 0 # 計算第幾次出場
    
    percentage = 0.1  # 10% = 0.1, 
    
    start_date =mdates.date2num(datetime.strptime(start_date_str,'%Y/%m/%d'))
    
    
    for idx, current_date in enumerate(K_date):
        if current_date > start_date:
            up = get_val_by_date(K_UD_date, K_up, current_date)
            down = get_val_by_date(K_UD_date, K_down, current_date)
            
            
            if K[idx]<down:
                K_down_date_list.append(current_date)
                K_down_val_list.append(close[idx]*0.99)
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 低檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            if K[idx]>up:
                K_up_date_list.append(current_date)
                K_up_val_list.append(close[idx]*1.01)             
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 高檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            #第一次買進
            if share_count == 0 and K[idx]<down:
                average_cost = close[idx]
                entry_count = 1
                share_count = 1
                buy_sum = close[idx]
                print ("{0} 買進 目前張數:{1:.2f}, 收盤價{6} 平均成本:{2:.2f}, 進場次數:{3:.2f}, 下次進場:{4:.2f}, 第一次出場:{5:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),average_cost*(1+percentage),close[idx]))
                
            #加碼買進，出現訊號，且虧損10%
            if share_count >0 and K[idx]<down and close[idx] < average_cost*(1-percentage):
                entry_count = entry_count +1
                add_shares = entry_count
                #print("加買張數 {}".format(add_shares))
                average_cost = (average_cost * share_count + close[idx]*add_shares)/(share_count + add_shares)
                share_count = share_count + add_shares
                buy_sum = buy_sum + close[idx]*add_shares
                if profit_stop_counter > 0:
                    profit_stop_counter = profit_stop_counter-1
                print ("{0} 買進 目前張數:{1:.2f}, 收盤價{6} 平均成本:{2:.2f}, 進場次數:{3:.2f}, 下次進場:{4:.2f}, 第一次出場:{5:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),average_cost*(1+percentage),close[idx]))
                
                #realized_profit = realized_profit + close[idx]-average_cost
                unrealized_profit = (close[idx] -average_cost)*share_count
                all_profit = (realized_profit+unrealized_profit)/buy_sum
                print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100))
            
            #賣出
            if share_count >0 and K[idx] > up:
                #計算停利點
                profit_stop = 9999
                if exit_count == 0 or profit_stop_counter == 0:
                    profit_stop_multiple =  (1+percentage)
                    profit_stop_counter = 0
                else:
                    profit_stop_multiple =  1+ (profit_stop_counter+1)*percentage
                profit_stop = profit_stop_multiple * average_cost
                #print(profit_stop , profit_stop_multiple , average_cost )
                if h[idx] > profit_stop:
                    profit_stop_counter = profit_stop_counter +1 
                    exit_count = exit_count +1 
                    del_shares = share_count/(entry_count - (exit_count-1)) 
                    #print("\n入場次數 {} 出場次數 {} ,賣出股數{}  分成{}".format(entry_count, exit_count,del_shares,(entry_count - (exit_count-1))))
                    
                    share_count = share_count -del_shares
                    sell_sum = sell_sum + close[idx]*del_shares
                    print ("{0} 賣出 目前張數:{1:.2f}, 倍數：{8:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f} 停利標準: {5:.2f}, 最高價:{6:.2f} 收盤價:{7:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*0.9,profit_stop, h[idx],close[idx],profit_stop_multiple))
                    
                    realized_profit = realized_profit + (close[idx]-average_cost)*del_shares
                    unrealized_profit = (close[idx] -average_cost)*share_count
                    all_profit = (realized_profit+unrealized_profit)/buy_sum
                    print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100))
                
                if share_count == 0:
                    average_cost = 0 # 平均成本
                    share_count  = 0  #持有張數
                    entry_count = 0 #進場次數
                    exit_count = 0 #出場次數
                    buy_sum = 0 # 買入總金額
                    sell_sum = 0 # 賣出總金額
                    unrealized_profit = 0 # 未實現損益 
                    realized_profit = 0 # 已實現損益 
                    print("")
    
    ax.plot_date(K_up_date_list, K_up_val_list,"rv")
    ax.plot_date(K_down_date_list, K_down_val_list,"g^")
    
#目前狀況
    if share_count > 0 :
        date_str = mdates.num2date(stock_obj.date[-1]).strftime("%Y/%m/%d")
        unrealized_profit = (close[-1] -average_cost)*share_count
        all_profit = (realized_profit+unrealized_profit)/buy_sum
        print ("{5}\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100,date_str))
    
def trade_model_guava_org(start_date_str, ax, stock_obj, K_date, K, K_UD_date, K_up, K_down):
    print("==org==")
    #定量買一張
    
    close = stock_obj.close
    h = stock_obj.high
    l = stock_obj.low
    
    K_up_date_list = []
    K_up_val_list = []
    K_down_date_list = []
    K_down_val_list = []
    
    average_cost = 0 # 平均成本
    share_count  = 0  #持有張數
    entry_count = 0 #進場次數
    exit_count = 0 #出場次數
    buy_sum = 0 # 買入總金額
    sell_sum = 0 # 賣出總金額
    unrealized_profit = 0 # 未實現損益 
    realized_profit = 0 # 已實現損益 
    percentage = 0.1  # 10% = 0.1, 
    
    #start_date_str = "2017/11/1"
    start_date =mdates.date2num(datetime.strptime(start_date_str,'%Y/%m/%d'))
    
    
    for idx, current_date in enumerate(K_date):
        if current_date > start_date:
            up = get_val_by_date(K_UD_date, K_up, current_date)
            down = get_val_by_date(K_UD_date, K_down, current_date)
            
            
            if K[idx]<down:
                K_down_date_list.append(current_date)
                K_down_val_list.append(close[idx]*0.99)
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 低檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            if K[idx]>up:
                K_up_date_list.append(current_date)
                K_up_val_list.append(close[idx]*1.01)             
                date_str = mdates.num2date(current_date).strftime("%Y/%m/%d")
                #print ("{0} 高檔, K={1}, up={2}, down={3}".format(date_str, K[idx], up, down))
                
            #第一次買進
            if share_count == 0 and K[idx]<down:
                average_cost = close[idx]
                entry_count = 1
                share_count = 1
                buy_sum = close[idx]
                print ("{0} 買進 目前張數:{1}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3:.2f}, 下次進場:{4:.2f}, 第一次出場:{5:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),average_cost*(1+percentage),close[idx]))
            #加碼買進，出現訊號，且虧損10%
            if share_count >0 and K[idx]<down and close[idx] < average_cost*(1-percentage):
                average_cost = (average_cost * share_count + close[idx])/(share_count + 1)
                entry_count = entry_count +1
                share_count = share_count +1
                buy_sum = buy_sum + close[idx]
                if exit_count > 0:
                    exit_count = exit_count - 1
                print ("{0} 買進 目前張數:{1}, 收盤價{6:.2f} 平均成本:{2:.2f}, 進場次數:{3:.2f}, 下次進場:{4:.2f}, 第一次出場:{5:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*(1-percentage),average_cost*(1+percentage),close[idx]))
                
                #realized_profit = realized_profit + close[idx]-average_cost
                unrealized_profit = (close[idx] -average_cost)*share_count
                all_profit = (realized_profit+unrealized_profit)/buy_sum
                print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100))
            
            #賣出
            if share_count >0 and K[idx] > up:
                #計算停利點
                profit_stop = 9999
                if exit_count == 0:
                    profit_stop_multiple =  (1+percentage)
                else:
                    #profit_stop_multiple =  (1+percentage) **(exit_count+1)
                    profit_stop_multiple =  1+ (exit_count+1)*percentage
                profit_stop = profit_stop_multiple * average_cost
                if h[idx] > profit_stop:
                    exit_count = exit_count +1 
                    share_count = share_count -1
                    sell_sum = sell_sum + close[idx]
                    print ("{0} 賣出 目前張數:{1:.2f}, 倍數：{8:.2f} 平均成本:{2:.2f}, 進場次數:{3}, 下次進場:{4:.2f} 停利標準: {5:.2f}, 最高價:{6:.2f} 收盤價:{7:.2f}".format(date_str, share_count,average_cost,entry_count,average_cost*0.9,profit_stop, h[idx],close[idx],profit_stop_multiple))
                    
                    realized_profit = realized_profit + close[idx]-average_cost
                    unrealized_profit = (close[idx] -average_cost)*share_count
                    all_profit = (realized_profit+unrealized_profit)/buy_sum
                    print ("\t\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100))
                
                if share_count == 0:
                    average_cost = 0 # 平均成本
                    share_count  = 0  #持有張數
                    entry_count = 0 #進場次數
                    exit_count = 0 #出場次數
                    buy_sum = 0 # 買入總金額
                    sell_sum = 0 # 賣出總金額
                    unrealized_profit = 0 # 未實現損益 
                    realized_profit = 0 # 已實現損益 
                    print("")
    
    ax.plot_date(K_up_date_list, K_up_val_list,"rv")
    ax.plot_date(K_down_date_list, K_down_val_list,"g^")

#目前狀況
    if share_count > 0 :
        date_str = mdates.num2date(stock_obj.date[-1]).strftime("%Y/%m/%d")
        unrealized_profit = (close[-1] -average_cost)*share_count
        all_profit = (realized_profit+unrealized_profit)/buy_sum
        print ("{5}\t總投入:{0:.2f} 總賣出:{1:.2f}，未實現損益:{2:.2f} , 已實現損益 {3:.2f}, 目前報酬 {4:.2f}%".format(buy_sum*1000, sell_sum*1000,unrealized_profit*1000,realized_profit*1000,all_profit*100,date_str))        


def caculate_model(sid, nday, sid_name,start_date_str="2018/1/1",adj_fix=False):
    print("")
    fname = "測試資料/台股/{0}d.csv".format(sid)
    s = stock(fname, adj_fix)
    s5 = stock_5day(fname, adj_fix)

    pulldown_date, pulldown = s.feature_pulldown(20*6) # 半年
    pd_date, pd_up, pd_down = tools.list_best_range(pulldown_date,pulldown, max = 0.99, min=0.4, n = 100)
    print("半年高檔拉回標準：", round(pd_down[-1],3), "目前：", round(pulldown[-1],3)) 
    
    BIAS = s.feature_BIAS(nday)
    bias_date, bias_up, bias_down = tools.list_best_range(s.date,BIAS, max = 0.8, min=0.2, n = 100)
    #bias_date, bias_up, bias_down = tools.list_best_range_std(s.date,BIAS,std_range=1.2, n = 100)
    
    BIAS_low = list(filter(lambda x: x < 0, BIAS[nday:]))
    print("主軸拉回標準：", round(tools.list_percentage(BIAS_low,0.4)*100,3), "目前：", round(BIAS[-1]*100,3)) 
        
    ma_d, ma = s.feature_MA(nday)
    k = s.feature_K()
#    k_date, k_up, k_down = tools.list_best_range(s.date,k,max = 0.9, min=0.1, n = 100)
    k_date, k_up, k_down = tools.list_best_range_std(s.date,k,std_range=1.25, n = 100)
    kma_d, kma = s.feature_K_MA(n=100)
    
    k5 = s5.feature_K()
#    k5_date, k5_up, k5_down = tools.list_best_range(s5.date,k5,max = 0.8, min=0.2, n = 100)
    k5_date, k5_up, k5_down = tools.list_best_range_std(s5.date,k5,std_range=1.25, n = 100)
    k5ma_d, k5ma = s5.feature_K_MA(n=100)
    
    #計算漲跌空間
    up_down_percent = s.feature_diff(n=30)
    percent_date, percent_up, percent_down = tools.list_best_range_std(s.date[50:],up_down_percent[50:],std_range=1.25, n = 100)
    
    #=====畫圖===========
    
    figure_num = 3 + 1 # 線圖需要佔兩個所以 + 1
    show_point_count = -600 # 要畫幾個點在圖上面。
    show_point_count = 0 # 要畫幾個點在圖上面。
    ax_list = []
    
    plt.close('all')
    fig = plt.figure()
    fig = plt.figure(figsize=(20,20))
    ax_tmp = plt.subplot2grid((figure_num, 1), (0, 0), rowspan=2)
    ax_list.append(ax_tmp)
    for i in range(2, figure_num):
        ax_tmp = plt.subplot2grid((figure_num, 1), (i, 0))
        ax_list.append(ax_tmp)
    fig_index = 0
    
    # K 線
    date_str = mdates.num2date(s.date[-1]).strftime("%m/%d")
    ax_list[fig_index].set_title("sid={0}, ma_len={1}, date={2}, price={3}".format(sid, nday, date_str, s.close[-1]))
    ax_list[fig_index].plot_date(s.date[show_point_count:], s.close[show_point_count:], "-")
    #ax_list[fig_index].plot_date(ma_d[show_point_count:], ma[show_point_count:], "-")
    ax_list[fig_index].grid()
    xlim_left, xlim_rignt = ax_list[fig_index].axes.get_xlim()
    fig_index = fig_index + 1
    
    # K
    date_str = mdates.num2date(k_date[-1]).strftime("%m/%d")
    ax_list[fig_index].set_title('date={0}, K={1}'.format(date_str, str(round(k[-1],2))))
    ax_list[fig_index].plot_date(s.date, k,"-")
    ax_list[fig_index].plot_date(kma_d, kma ,"-")
    ax_list[fig_index].plot_date(k_date, k_up,"-")
    ax_list[fig_index].plot_date(k_date, k_down,"-")
    #ax_list[fig_index].plot_date([k_date[0],k_date[-1]], [80,80],"-")
    #ax_list[fig_index].plot_date([k_date[0],k_date[-1]], [20,20],"-")
    ax_list[fig_index].text(k_date[-1], k_up[-1], round(k_up[-1],2))
    ax_list[fig_index].text(k_date[-1], k_down[-1], round(k_down[-1],2))
    ax_list[fig_index].axes.set_xlim(xlim_left, xlim_rignt)
    ax_list[fig_index].grid()
    fig_index = fig_index + 1

    #漲跌區間
    ax_list[fig_index].set_title('up down percent')
    ax_list[fig_index].plot_date(percent_date, percent_up,"-")
    ax_list[fig_index].plot_date(percent_date, percent_down,"-")
    ax_list[fig_index].axes.set_xlim(xlim_left, xlim_rignt)
    ax_list[fig_index].grid()   
    fig_index = fig_index + 1    
    
    
    # 5日 K
#    date_str = mdates.num2date(k5_date[-1]).strftime("%m/%d")
#    ax_list[fig_index].set_title('date={0}, 5day K={1}'.format(date_str, str(round(k5[-1],2))))
#    ax_list[fig_index].plot_date(s5.date, k5,"-")
#    ax_list[fig_index].plot_date(k5ma_d, k5ma ,"-")
#    ax_list[fig_index].plot_date(k5_date, k5_up,"-")
#    ax_list[fig_index].plot_date(k5_date, k5_down,"-")
#    ax_list[fig_index].text(k5_date[-1], k5_up[-1], round(k5_up[-1],2))
#    ax_list[fig_index].text(k5_date[-1], k5_down[-1], round(k5_down[-1],2))
#    ax_list[fig_index].text(k5_date[-1], 0 , date_str)
#    ax_list[fig_index].axes.set_xlim(xlim_left, xlim_rignt)
#    ax_list[fig_index].grid()
#    fig_index = fig_index + 1
    
    #高檔拉回
#    ax_list[fig_index].set_title('pull down')
#    ax_list[fig_index].plot_date(pulldown_date, pulldown,"-")
#    ax_list[fig_index].plot_date(pd_date, pd_down,"-")
#    ax_list[fig_index].axes.set_xlim(xlim_left, xlim_rignt)
#    ax_list[fig_index].grid()   
#    fig_index = fig_index + 1    
#    
#    #BIAS
#    ax_list[fig_index].set_title('BIAS')
#    ax_list[fig_index].plot_date(s.date[100:], BIAS[100:],"-")
#    #ax_list[fig_index].plot_date(bias_date[50:], bias_up[50:],"-")
#    ax_list[fig_index].plot_date(bias_date[50:], bias_down[50:],"-")
#    ax_list[fig_index].axes.set_xlim(xlim_left, xlim_rignt)
#    ax_list[fig_index].grid()
#    fig_index = fig_index + 1
    
    
    #trade_model_guava_org(start_date_str, ax_list[0], s, s.date, k, k_date, k_up, k_down) # <= 大跌時攤平效果不好
    #trade_model_guava_v1(start_date_str, ax_list[0], s, s.date, k, k_date, k_up, k_down)# <= 大跌時攤平效果不好
    #trade_model_guava_v2(start_date_str, ax_list[0], s, s.date, k, k_date, k_up, k_down)  # <= 適合, 
    #trade_model_guava_v2_1(start_date_str, ax_list[0], s, s.date, k, k_date, k_up, k_down)  # <= 不行
    #trade_model_guava_v2_2(start_date_str, ax_list[0], s, s.date, k, k_date, k_up, k_down, percent_date, percent_up, percent_down)  # <= 0050, 2007/9/1 , 累積 512張
    #trade_model_guava_v2_3(start_date_str, ax_list[0], s, s.date, k, k_date, k_up, k_down, percent_date, percent_up, percent_down)  # <= 最適合
    #trade_model_guava_v2_4(start_date_str, ax_list[0], s, s.date, k, k_date, k_up, k_down, percent_date, percent_up, percent_down)  # <= 最適合, 金字塔出場
    trade_model_guava_v2_5(start_date_str, ax_list[0], s, s.date, k, k_date, k_up, k_down, percent_date, percent_up, percent_down)  # <= 最適合, 金字塔出場, 第二天開盤價買入
    #trade_model_guava_v3(start_date_str, ax_list[0], s, s.date, k, k_date, k_up, k_down) # <= 資金壓力太大
    
    plt.tight_layout()
#    plt.show()
#    plt.savefig('out/{0}-{2}-{1}.png'.format(sid, datetime.now().strftime("%m-%d"),sid_name), dpi=199) # 不顯示存圖

            
def get_nday(sid):
    for config in Configs:
        if(sid == config['sid']):
            print ("\r\n *-*-*-*-*-*-* ",config['sid'], config['S_name'], "均線：", config['best_ma'], "*-*-*-*-*-*-*")
            return config['best_ma']


    
if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        sid = sys.argv[1]
        nday = get_nday(sid)
        caculate_model(sid, nday , "d",False)
    else:
        for config in Configs:
            print("\r\n")
            print(Fore.CYAN + Back.MAGENTA + Style.BRIGHT + " *-*-*-*-*-*-*  {0} {1} 均線：{2} *-*-*-*-*-*-*".format(config['sid'], config['S_name'],config['best_ma'] ))
            if config['Update'] == "yahoo":
                adj_fix = True
            else:
                adj_fix = False
            sid = config['sid']
            nday = config['best_ma'] #設定主軸
            caculate_model(sid, nday,config['S_name'],config['test_start_date'],adj_fix=adj_fix)
            #break;
    
    
    if hasattr(sys, '_MEIPASS'):
        input("按任意鍵結束")