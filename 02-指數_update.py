import datetime
import time
import sys
import config_stock_tw

from pandas_datareader import data as pdr
import fix_yahoo_finance as yf
yf.pdr_override() # <== that's all it takes :-)


def update_index(sid, n_year):
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    # n 年的資料
    start_date = (datetime.datetime.now()- datetime.timedelta(days=n_year*365)).strftime('%Y-%m-%d')
    SID = sid
    out_file = "測試資料/台股/{0}d.csv".format(SID)
    

    def true_val(current_date, current_val, dividend_dataframe):
        return current_val  # 不還原權值, adj close 就是還原值了
        ret = current_val
        for idx, dividend_date in enumerate(dividend_dataframe.index.values):
            if dividend_date <= current_date:
                ret = ret + dividend_dataframe.iloc[idx][0]
        return ret

    # 分紅資料
    dividend_dataframe = pdr.get_data_yahoo(SID, start=start_date, end=end_date,actions='only')
    # print(dividend_dataframe)
    time.sleep(1)

    # 日K 資料
    data = pdr.get_data_yahoo(SID, start=start_date, end=end_date)

    for idx, current_date  in enumerate(data.index.values):
        o = true_val(current_date, data.iloc[idx][0], dividend_dataframe)
        h = true_val(current_date, data.iloc[idx][1], dividend_dataframe)
        l = true_val(current_date, data.iloc[idx][2], dividend_dataframe)
        c = true_val(current_date, data.iloc[idx][3], dividend_dataframe)
        #print(current_date,data.iloc[idx][0], o)
        data.set_value(current_date,"Open",o)
        data.set_value(current_date,"High",h)
        data.set_value(current_date,"Low",l)
        data.set_value(current_date,"Close",c)
        #print(idx, current_date, data.iloc[idx][0], data.iloc[idx][1], data.iloc[idx][2], data.iloc[idx][3], data.iloc[idx][4], data.iloc[idx][5])

    print(len(data.index.values))
    data.to_csv(out_file, sep=',', encoding='utf-8')


    # download Panel
    #= pdr.get_data_yahoo(["SPY", "IWM"], start="2017-01-01", end="2017-04-30")
    #print(data3)
    time.sleep(3)

            
if __name__ == '__main__':
    Configs = config_stock_tw.Configs
    
    if len(sys.argv) > 1:
        sid = sys.argv[1]
        nday = get_nday(sid)
        caculate_model(sid, nday)
    else:
        for config in Configs:
            if(config['Update'] == "yahoo"):
                print ("\r\n *-*-*-*-*-*-* ",config['Update'], config['sid'], config['S_name'], "均線：", config['best_ma'], "*-*-*-*-*-*-*")
                sid = config['sid']
                #update_index(sid, 5)  # 5年
                update_index(sid, 10) # 10年
                #break