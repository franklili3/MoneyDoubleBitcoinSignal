#import random
#from datetime import datetime, timedelta
from data_generator import generate_random_series
import dash_tvlwc
import dash
#from dash.dependencies import Input, Output, State
from dash import html, dcc#, ctx

from dash_tvlwc.types import ColorType, SeriesType
import os
import requests, json
import sys
sys.path.append('..')
#import app

import logging
from flask_caching import Cache
from logging.handlers import RotatingFileHandler

dash.register_page(__name__,
    title='4.比特币价格上限和下限分析',
    name='4.比特币价格上限和下限分析')
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
    #print('username: ', username)
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
        data_price = []
        data_price_lower_limit = []
        data_price_upper_limit = []

        for i in range(1,12):
            query_predicted_marketcap_log = "?fields=date,price,price_lower_limit,price_upper_limit&&perPage=500&&page=" + str(i)#&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
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
                time = item['date']
                value1 = item['price']
                value2 = item['price_lower_limit']
                value3 = item['price_upper_limit']
                #app1.logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)) + ' ,value3:{}'.format(str(value3)))
                #print('time: ', time, ', value: ', value)
                data_price.append({'time': time, 'value': value1})
                data_price_lower_limit.append({'time': time, 'value': value2})
                data_price_upper_limit.append({'time': time, 'value': value3})
        data = [data_price, data_price_lower_limit, data_price_upper_limit]
    else:
        data = [generate_random_series(5000, n=5000), generate_random_series(5000, n=5000), generate_random_series(5000, n=5000)]

    return data
data1 = get_upper_lower_price()
app1.logger.debug('data1[0]: {}'.format(str(data1[0][0:10])))
app1.logger.debug('data1[1]: {}'.format(str(data1[1][0:10])))
app1.logger.debug('data1[2]: {}'.format(str(data1[2][0:10])))
main_panel = [
    html.Div(style={'position': 'relative', 'width': '100%', 'height': '100%', 'marginBottom': '30px'}, children=[
        html.Div(children=[
            dash_tvlwc.Tvlwc(
                #id='tv-chart-1',
                #seriesData=[generate_random_ohlc(1000, n=1000)],
                #seriesTypes=[SeriesType.Candlestick],
                seriesData=[data1[0], data1[1], data1[2]],
                seriesTypes=[SeriesType.Line, SeriesType.Line, SeriesType.Line],
                width='99%',
                chartOptions={
                    'layout': {
                        'background': {'type': ColorType.Solid, 'color': '#1B2631'},
                        'textColor': 'white',
                    },
                    'grid': {
                        'vertLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
                        'horzLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
                    },
                    'localization': {
                        'locale': 'zh-CN',
                        #en-US
                        'priceFormatter': "(function(price) { return '$' + price.toFixed(2); })"
                        # 
                    }
                    
                    #},
                    #'rightPriceScale': {
                    #    'visible': 'true'
                    #},
                    #'leftPriceScale': {
                    #    'visible': 'true'
                    
                },
                seriesOptions=[
                    {
                        'title': '比特币价格',
                        #'color': 'blue' 
                        #'priceScaleId': 'left'
                    },
                    {
                        'title': '比特币价格下限',
                        'color': 'green' 
                        #'priceScaleId': 'left'
                    },
                    {
                        'title': '比特币价格上限',
                        'color': 'red' 
                    }
                ]
            ),
        ], style={'width': '100%', 'height': '100%', 'left': 0, 'top': 0}),
        html.Div(id='chart-info', children=[
            html.Span(id='chart-price', style={'fontSize': '60px', 'fontWeight': 'bold'}),
            html.Span(id='chart-date', style={'fontSize': 'small'}),
        ], style={'position': 'absolute', 'left': 0, 'top': 0, 'zIndex': 10, 'color': 'white', 'padding': '10px'})
    ])
]

layout = html.Div([
    #dcc.Interval(id='timer', interval=500),
    html.Div(className='container', children=[
        html.Div(className='main-container', children=[
            html.H2('比特币价格上限和下限图 📊'),
            dcc.Markdown('''
            ### 根据历史经验，比特币市值偏差为1时，比特币市值在牛市顶部，计算出的比特币价格为牛市的价格上限，比特币市值偏差为-0.95时，比特币市值在熊市底部，计算出的比特币价格为熊市的价格下限。
            '''),
            html.Div(children=main_panel)
        ]),
        html.Span('李力, 2024')
    ])
])


