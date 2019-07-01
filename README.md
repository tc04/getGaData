editor: Tony Chiu

datetime: 2019-07-01

# GA API 
使用 Google Analytics Reporting API v4 來呼叫 GA 的資料，目前規劃是將接收到資料儲存成 csv 的格式，透過 MariaDB 提供的 import data API 來作傳入的動作


## 建立憑證

1. 建立 google API 的應用程式專案 [[>]](https://console.developers.google.com/start/api?id=analyticsreporting.googleapis.com&credential=client_key)，如果已經有專案就直接**選取專案**
2. 左上角選單選取 **API 和服務** — **主頁**，啟用 **API 和服務** (開啟 `Analytic Reporting API, Google Analytic API` )
3. 到**憑證** — **Oauth 同意畫面**中設置名字並設置 API 範圍 ( `analytics.readonly` ) [[>]](https://console.cloud.google.com/apis/credentials/consent?pli=1&project=erudite-scarab-244203&folder&organizationId&duration=P1D)
4. 建立憑證，類型勾取"其他"，並命名就完成了 [[>]](https://console.developers.google.com/apis/credentials)
5. 進入該憑證並且下載密鑰(官方推薦下載 json 格式的)，並命名為 `client_secrets.json`
6. 將帳號加入 GA 權限

## 測試環境

- 作業系統環境為 window 10
    - Python 3.7 (anaconda)
        - oauth2client
        - google-api-python-client

## 執行

執行時須帶入 viewID 和 queryTimeRange

例: python main.py 1000001 2019-06-25/2019-06-25

透過讀取 query_string.json 來給定 query GA 所需的 info 以及 [insert MariaDB 的 insert string] (恕刪)
