#import random
#from datetime import datetime, timedelta
from data_generator import generate_random_series
import dash_tvlwc
#import dash
from dash.dependencies import Input, Output

from dash import html, clientside_callback, dcc, register_page, get_app#, callback, ctx

from dash_tvlwc.types import ColorType, SeriesType
import os
import requests, json
#from flask import request
from user_agents import parse
#import sys
#sys.path.append('..')
#import app

import logging
from flask_caching import Cache
from logging.handlers import RotatingFileHandler
#import dash_bootstrap_components as dbc
from flask_login import current_user
from utils.login_handler import require_login
from flask import session

register_page(__name__,
    title='1.比特币因子',
    name='1.比特币因子-客户')
require_login(__name__)
app1 = get_app()

# 创建FileHandler，并添加到logger.handlers列表
logger = logging.getLogger(__name__)
handler = logging.FileHandler('error.log')
logger.setLevel(logging.DEBUG)#)INFO
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
handler.setFormatter(formatter)  
logger.addHandler(handler)

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


def layout(**kwargs):
    if not current_user.is_authenticated:
        return html.Div(["请", dcc.Link("登录", href="/login"), "，再继续访问"])

    return html.Div(
        [
            #dcc.Interval(id='timer', interval=500),
            dcc.Store(id="store-6"),
            html.Div(className='container', children=[
                html.Div([
                    html.Div([
                        html.Div([
                            dcc.Link("主页", href="/home-client"),
                            html.Br(),
                            dcc.Link("2.比特币预测市值", href="/bitcoin-predicted-marketcap-client"),
                            html.Br(),
                            dcc.Link("3.比特币市值偏离度", href="/bitcoin-marketcap-bias-client"),
                            html.Br(),
                            dcc.Link("4.比特币市值上限和下限", href="/bitcoin-upper-lower-marketcap-client"),
                            html.Br(),
                            dcc.Link("5.比特币价格上限和下限", href="/bitcoin-upper-lower-price-client"),
                            html.Br(),
                            dcc.Link("6.我的累计收益率", href="/my-total-return-client")
                    ])
                        #    dcc.Link(f"{page['name']}", href=page["relative_path"])# - {page['path']}
                        #) for page in page_registry.values()
                    ]),            
                ]),
                html.Div(className='main-container', children=[
                    html.H2('比特币因子和市值图 📊'),
                    html.H3('对比特币市值影响最大的因子是比特币区块数，比特币区块数和市值的走势很一致，相关系数高达0.9。'),
                    html.Div(id="main_panel-6")
                ]),
                html.Span('李力, 2024')
            ])
        ])

clientside_callback(
    """
    function(trigger) {
        //  can use any prop to trigger this callback - we just want to store the info on startup
        // USE THIS TO GET screen dimensions 
        // const screenInfo = {height :screen.height, width: screen.width};  
        // USE THIS TO GET useragent string
        user_Agent = navigator.userAgent;
        return user_Agent
    }
    """,
    Output("store-6", "data"),
    Input("store-6", "data"),
)

@app1.callback(Output("main_panel-6", "children"), Input("store-6", "data"))
def update(JSoutput):
    TIMEOUT = 60 * 60 * 24
    @cache.memoize(timeout=TIMEOUT)
    def get_series_client(frequency='weekly'):
        home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'
        '''
        auth_path = '/api/admins/auth-with-password'
        auth_url = home_url + auth_path
        username = os.environ.get('admin_username')
        #print('username: ', username)
        password = os.environ.get('admin_password')
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
        '''
        if session.get('token'):
            token = session.get('token')
            #print('token: ', token)

            # 使用已经登录获取到的token 发送一个get请求
            get_path = '/api/collections/bitcoin_trade_signal/records'
            data_marketcap_log = []
            data_blocks_log = []
            if frequency == 'monthly':
                for i in range(1,15):        
                    query_bitcoin_marketcap_log = "?filter=(day_of_month=1)&&fields=date,marketcap_log,blocks_log&&perPage=12&&page=" + str(i)#&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
                    get_url = home_url + get_path + query_bitcoin_marketcap_log
                    header2 = {
                        "Content-Type": "application/json",
                        "Authorization": token
                    }
                    response2 = requests.get(get_url, headers=header2)
                    response2_json = response2.json()
                    response2_str = str(response2_json)
                    logger.debug('response2_str: {}'.format(response2_str))
                    for item in response2_json['items']:
                        time = item['date']
                        value1 = item['marketcap_log']
                        value2 = item['blocks_log']
                        logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)))
                        #print('time: ', time, ', value: ', value)
                        data_marketcap_log.append({'time': time, 'value': value1})
                        data_blocks_log.append({'time': time, 'value': value2})
                    data = [data_marketcap_log, data_blocks_log]
            elif frequency == 'weekly':
                for i in range(1,15):
                    query_bitcoin_marketcap_log = "?filter=(weekday=1)&&fields=date,marketcap_log,blocks_log&&perPage=52&&page=" + str(i)#&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
                    get_url = home_url + get_path + query_bitcoin_marketcap_log
                    header2 = {
                        "Content-Type": "application/json",
                        "Authorization": token
                    }
                    response2 = requests.get(get_url, headers=header2)
                    response2_json = response2.json()
                    response2_str = str(response2_json)
                    logger.debug('response2_str: {}'.format(response2_str))
                    for item in response2_json['items']:
                        time = item['date']
                        value1 = item['marketcap_log']
                        value2 = item['blocks_log']
                        logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)))
                        #print('time: ', time, ', value: ', value)
                        data_marketcap_log.append({'time': time, 'value': value1})
                        data_blocks_log.append({'time': time, 'value': value2})
                data = [data_marketcap_log, data_blocks_log]
        else:
            data = [generate_random_series(5000, n=500), generate_random_series(5000, n=500)]

        return data
    user_agent = parse(JSoutput)
    is_mobile = user_agent.is_mobile
    is_tablet = user_agent.is_tablet
    is_pc = user_agent.is_pc
    if is_pc:
        data1 = get_series_client(frequency='weekly')
    elif is_mobile or is_tablet:
        data1 = get_series_client(frequency='monthly') 

    logger.debug('data1[0]: {}'.format(str(data1[0])[0:10]))
    logger.debug('data1[1]: {}'.format(str(data1[1])[0:10]))
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
    return main_panel