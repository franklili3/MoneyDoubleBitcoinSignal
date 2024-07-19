import os
import requests, json
import pandas as pd
import datetime

home_url = 'http://127.0.0.1:8090/' #'https://pocketbase-5umc.onrender.com' 
auth_path = '/api/admins/auth-with-password'
auth_url = home_url + auth_path
username = os.environ.get('username')
#print('username: ', username)
password = os.environ.get('password')
# json.dumps 将python数据结构转换为JSON
data1 = json.dumps({"identity": username, "password": password})
# Content-Type 请求的HTTP内容类型 application/json 将数据已json形式发给服务器
header1 = {"Content-Type": "application/json"}
response1 = requests.post(auth_url, data=data1, headers=header1)
response1_json = response1.json()
#print('html: ', html)

# html.json JSON 响应内容，提取token值
if response1_json['token']:
    token = response1_json['token']

    # 使用已经登录获取到的token 发送一个post请求
    post_path = '/api/collections/bitcoin_trade_signal/records'
    
    post_url = home_url + post_path
    header2 = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    btc_market_cap_and_factor = pd.read_excel('btc_market_cap_and_factor0528.xlsx', header=0, parse_dates=[0])
    btc_market_cap_and_factor['date_str'] = btc_market_cap_and_factor['date'].apply(lambda x: datetime.datetime.strftime(x,'%Y-%m-%d %H:%M:%S'))
    #print(btc_market_cap_and_factor.dtypes)
    btc_market_cap_and_factor1 = btc_market_cap_and_factor.drop('date', axis=1)
    print(btc_market_cap_and_factor1.dtypes)
    btc_market_cap_and_factor1 = btc_market_cap_and_factor1.rename(columns = {'date_str': 'date'})

    for index, row in btc_market_cap_and_factor1.iterrows():
        if index == 0:
            row_json = row.to_json()
            print('row_json: ', row_json)
            response2 = requests.post(post_url, headers=header2, data=row_json)
            response2_json = response2.json()
            if response2.status_code == 200:
                print('post data success.')
            else:
                print('response2_json: ', response2_json)
        