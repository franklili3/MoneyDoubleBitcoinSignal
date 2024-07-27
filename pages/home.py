import dash
from dash import html
import dash_daq as daq
import requests, json
import logging
from flask_caching import Cache
from logging.handlers import RotatingFileHandler
import os

dash.register_page(__name__, 
    path='/',
    title='主页',
    name='主页')
app1 = dash.get_app()
# 创建RotatingFileHandler，并添加到app.logger.handlers列表
handler = RotatingFileHandler('error.log', maxBytes=100000, backupCount=10)
handler.setLevel(logging.INFO)#)DEBUG
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
handler.setFormatter(formatter)  

# 配置日志等级
app1.logger.setLevel(logging.INFO)#)DEBUG

app1.logger.addHandler(handler)
if 'REDIS_URL' in os.environ:
    
    # Use Redis if REDIS_URL set as an env variable
    cache = Cache(app1.server, config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
    })
else:
    pass
    # Diskcache for non-production apps when developing locally
    cache = Cache(app1.server, config={
        'CACHE_TYPE': 'filesystem',
        'CACHE_DIR': 'cache-directory'
    })


TIMEOUT = 60 * 60 * 24
@cache.memoize(timeout=TIMEOUT)
def get_upper_lower_price():
    home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'
    auth_path = '/api/admins/auth-with-password'
    auth_url = home_url + auth_path
    username = os.environ.get('username')
    print('username: ', username)
    app1.logger.debug('username: ', username)
    password = os.environ.get('password')
    # json.dumps 将python数据结构转换为JSON
    data1 = json.dumps({"identity": username, "password": password})
    # Content-Type 请求的HTTP内容类型 application/json 将数据已json形式发给服务器
    header1 = {"Content-Type": "application/json"}
    response1 = requests.post(auth_url, data=data1, headers=header1)
    response1_json = response1.json()
    response1_str = str(response1_json)
    #print('html: ', html)
    app1.logger.debug('response1_str: {}'.format(response1_str[0:100]))
    # html.json JSON 响应内容，提取token值
    if response1_json['token']:
        token = response1_json['token']

        # 使用已经登录获取到的token 发送一个get请求
        get_path = '/api/collections/bitcoin_trade_signal/records'

        query_predicted_marketcap_log = "?fields=date,price,price_lower_limit,price_upper_limit&&perPage=500&&page=11"#&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
        get_url = home_url + get_path + query_predicted_marketcap_log
        header2 = {
            "Content-Type": "application/json",
            "Authorization": token
        }
        response2 = requests.get(get_url, headers=header2)
        response2_json = response2.json()
        response2_str = str(response2_json)
        app1.logger.debug('response2_str: {}'.format(response2_str[0:100]))
        for item in response2_json['items']:
            time = item['date'][0:10]
            data_price = item['price']
            data_price_lower_limit = item['price_lower_limit']
            data_price_upper_limit = item['price_upper_limit']
            #app1.logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)) + ' ,value3:{}'.format(str(value3)))
            #print('time: ', time, ', value: ', value)

            
        data = [time, data_price, data_price_lower_limit, data_price_upper_limit]
    else:
        data = ["2024-07-22", 39877, 229876]

    return data
data1 = get_upper_lower_price()
app1.logger.debug('data1[0]: {}'.format(str(data1[0][0:10])))
app1.logger.debug('data1[1]: {}'.format(str(data1[1][0:10])))
app1.logger.debug('data1[2]: {}'.format(str(data1[2][0:10])))
layout = html.Div([
    html.H2('最新数据-' + data1[0]),
    daq.Gauge(
        value=data1[1],
        label='Default',
        max=data1[3],
        min=data1[2],
    )
])