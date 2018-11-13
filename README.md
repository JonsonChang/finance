## 說明
- 每日一鍵更新股價資訊
- 依不停損投資模型計算出當日關鍵參數，並顯示投資操作方法。
- 本程式並無自動下單功能，請到進出場指示時，請在第二天開盤時自行下單。
- 不停損投資模型為一個攤平加碼的策略，在不清楚投資策略前，請勿跟著程式下單。


![image](https://raw.githubusercontent.com/JonsonChang/finance/master/readme_pic/Image%201.png)

## 程式環境
- python3

## 使用方式：
### 設定要追蹤的股票代號
使用文字編輯器修改檔案  config_stock_tw.py

### 執行程式

```sh
python 00-test_台股_update.py  #到證交所更新目前最新的股價
python 02-指數_update.py  #更新指數資料，資料來源 yahoo finance
python 00-test_台股_不停損投資模型.py  #輸出投資的操作方法，比如應該要買，應該要賣，還是不動作
```


## 其他
其他功能目前比較少用，有空再寫文件。
