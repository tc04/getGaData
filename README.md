editor: Tony Chiu
datetime: 2019-06-28

# GA API 
使用 Google Analytics Reporting API v4 來呼叫 GA 的資料
目前規劃是將接收到資料儲存成 csv 的格式，透過 MariaDB 提供
的 import data API 來作傳入的動作


## 執行

執行時須帶入 viewID 和 queryTimeRange
例: python main.py 1000001 2019-06-25/2019-06-25

目前撰寫到 query 資料回來並整理好成一個 list

會讀取 analyticsreporting.dat，如果沒有授權
使用 client_secrets.json，重新進行驗證

透過讀取 query_string.json 來給定 query GA 所需的 info
以及 insert MariaDB 的 insert string (恕刪)