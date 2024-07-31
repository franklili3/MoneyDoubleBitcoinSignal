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
#from flask import request
#from user_agents import parse
#import sys
#sys.path.append('..')
#import app

import logging
from flask_caching import Cache
from logging.handlers import RotatingFileHandler
import dash_bootstrap_components as dbc

dash.register_page(__name__,
    title='1.比特币因子分析',
    name='1.比特币因子分析')
app1 = dash.get_app()
# 创建RotatingFileHandler，并添加到app.logger.handlers列表
handler = RotatingFileHandler('../error.log', maxBytes=100000, backupCount=10)
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
def get_series(frequency='weekly'):
    home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'
    auth_path = '/api/admins/auth-with-password'
    auth_url = home_url + auth_path
    username = os.environ.get('username')
    #print('username: ', username)
    password = os.environ.get('password')
    #print('password: ', password)
    # json.dumps 将python数据结构转换为JSON
    data1 = json.dumps({"identity": username, "password": password})
    # Content-Type 请求的HTTP内容类型 application/json 将数据已json形式发给服务器
    header1 = {"Content-Type": "application/json"}
    response1 = requests.post(auth_url, data=data1, headers=header1)
    response1_json = response1.json()
    response1_str = str(response1_json)
    #print('html: ', html)
    #print('response1_str: {}'.format(response1_str))
    app1.logger.debug('response1_str: {}'.format(response1_str))
    # html.json JSON 响应内容，提取token值
    if response1_json['token']:
        token = response1_json['token']

        # 使用已经登录获取到的token 发送一个get请求
        get_path = '/api/collections/bitcoin_trade_signal/records'
        data_marketcap_log = []
        data_blocks_log = []
        if frequency == 'daily':
            for i in range(1,12):
                query_bitcoin_marketcap_log = "?fields=date,marketcap_log,blocks_log&&perPage=500&&page=" + str(i)#&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
                get_url = home_url + get_path + query_bitcoin_marketcap_log
                header2 = {
                    "Content-Type": "application/json",
                    "Authorization": token
                }
                response2 = requests.get(get_url, headers=header2)
                response2_json = response2.json()
                response2_str = str(response2_json)
                app1.logger.debug('response2_str: {}'.format(response2_str))
                for item in response2_json['items']:
                    time = item['date']
                    value1 = item['marketcap_log']
                    value2 = item['blocks_log']
                    app1.logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)))
                    #print('time: ', time, ', value: ', value)
                    data_marketcap_log.append({'time': time, 'value': value1})
                    data_blocks_log.append({'time': time, 'value': value2})
            data = [data_marketcap_log, data_blocks_log]
        elif frequency == 'weekly':
            for i in range(1,3):
                query_bitcoin_marketcap_log = "?filter=(weekday=1)&&fields=date,marketcap_log,blocks_log&&perPage=500&&page=" + str(i)#&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
                get_url = home_url + get_path + query_bitcoin_marketcap_log
                header2 = {
                    "Content-Type": "application/json",
                    "Authorization": token
                }
                response2 = requests.get(get_url, headers=header2)
                response2_json = response2.json()
                response2_str = str(response2_json)
                app1.logger.debug('response2_str: {}'.format(response2_str))
                for item in response2_json['items']:
                    time = item['date']
                    value1 = item['marketcap_log']
                    value2 = item['blocks_log']
                    app1.logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)))
                    #print('time: ', time, ', value: ', value)
                    data_marketcap_log.append({'time': time, 'value': value1})
                    data_blocks_log.append({'time': time, 'value': value2})
            data = [data_marketcap_log, data_blocks_log]
    else:
        data = [generate_random_series(5000, n=5000), generate_random_series(5000, n=5000)]

    return data
'''
user_agent_string = request.headers.get('User-Agent')
user_agent = parse(user_agent_string)
is_mobile = user_agent.is_mobile
is_tablet = user_agent.is_tablet
is_pc = user_agent.is_pc
if is_pc:
    data1 = get_series(frequency='daily')
elif is_mobile or is_tablet:
    data1 = get_series(frequency='weekly') 
'''
data1 = get_series(frequency='weekly')   
app1.logger.debug('data1[0]: {}'.format(str(data1[0])[0:10]))
app1.logger.debug('data1[1]: {}'.format(str(data1[1])[0:10]))
main_panel = [
    html.Div(style={'position': 'relative', 'width': '100%', 'height': '100%', 'marginBottom': '30px'}, children=[
        html.Div(children=[
            dash_tvlwc.Tvlwc(
                #id='tv-chart-1',
                #seriesData=[generate_random_ohlc(1000, n=1000)],
                #seriesTypes=[SeriesType.Candlestick],
                seriesData=[data1[0], data1[1]],
                seriesTypes=[SeriesType.Line, SeriesType.Line],
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
                        'priceFormatter': "(function(price) { return price.toFixed(2); })"
                        #'$' + 
                    },
                    'rightPriceScale': {
                        'visible': 'true'
                    },
                    'leftPriceScale': {
                        'visible': 'true'
                    }
                },
                seriesOptions=[
                    {
                        'title': '比特币市值(对数)',
                        #'color': 'blue' 
                        'priceScaleId': 'left'
                    },
                    {
                        'title': '比特币区块数(对数)',
                        'color': '#FFAA30' 
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
                    html.H2('比特币因子和市值图 📊'),
                    dcc.Markdown('''
                    ### 对比特币市值影响最大的因子是比特币区块数，比特币区块数和市值的走势很一致，相关系数高达0.9。
                    '''),
                    html.Div(children=main_panel)
                ]),
                html.Span('李力, 2024')
            ])
        ])



