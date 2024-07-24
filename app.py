import random
from datetime import datetime, timedelta

import dash_tvlwc
import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc, ctx

from dash_tvlwc.types import ColorType, SeriesType
from data_generator import generate_random_ohlc, generate_random_series

from flask_caching import Cache
import os
import requests, json, logging
from logging.handlers import RotatingFileHandler

#logger = logging.getLogger(__name__)
app = dash.Dash(__name__)
server = app.server
# 配置日志等级
app.logger.setLevel(logging.INFO)#)DEBUG

# 创建RotatingFileHandler，并添加到app.logger.handlers列表
handler = RotatingFileHandler('error.log', maxBytes=100000, backupCount=10)
handler.setLevel(logging.INFO)#)DEBUG
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
handler.setFormatter(formatter)  
app.logger.addHandler(handler)
if 'REDIS_URL' in os.environ:
    
    # Use Redis if REDIS_URL set as an env variable
    cache = Cache(app.server, config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
    })
else:
    pass
    # Diskcache for non-production apps when developing locally
    cache = Cache(app.server, config={
        'CACHE_TYPE': 'filesystem',
        'CACHE_DIR': 'cache-directory'
    })

TIMEOUT = 60 * 60 * 24
@cache.memoize(timeout=TIMEOUT)
def generate_series():
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
    app.logger.debug('response1_str: {}'.format(response1_str))
    # html.json JSON 响应内容，提取token值
    if response1_json['token']:
        token = response1_json['token']

        # 使用已经登录获取到的token 发送一个get请求
        get_path = '/api/collections/bitcoin_trade_signal/records'
        data_marketcap_log = []
        data_blocks_log = []

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
            app.logger.debug('response2_str: {}'.format(response2_str))
            for item in response2_json['items']:
                time = item['date']
                value1 = item['marketcap_log']
                value2 = item['blocks_log']
               
                app.logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)))
                #print('time: ', time, ', value: ', value)
                data_marketcap_log.append({'time': time, 'value': value1})
                data_blocks_log.append({'time': time, 'value': value2})
        data = [data_marketcap_log, data_blocks_log]
    else:
        data = [generate_random_series(5000, n=5000), generate_random_series(5000, n=5000)]

    return data
data1 = generate_series()
app.logger.debug('data1[0]: {}'.format(str(data1[0])))
app.logger.debug('data1[1]: {}'.format(str(data1[1])))
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
                    }
                },
                seriesOptions=[
                    {
                        'title': 'Bitcoin MarketCap(Log)'
                        #'color': 'blue' 
                    },
                    {
                        'title': 'Number of Bitcoin Blocks(Log)',
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

app.layout = html.Div([
    dcc.Interval(id='timer', interval=500),
    html.Div(className='container', children=[
        html.Div(className='main-container', children=[
            html.H1('翻一番比特币市值图 📊'),
            dcc.Markdown('''
            ## 比特币市值的涨跌周期为4年，每个周期中都有1个牛市顶部和1个熊市底部。
            '''),
            html.Div(children=main_panel)
        ]),
        html.Span('李力, 2024')
    ])
])


if __name__ == '__main__':
    app.run(debug=False)