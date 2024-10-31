#import random
#from datetime import datetime, timedelta
from data_generator import generate_random_series
import dash_tvlwc
#import dash
from dash.dependencies import Input, Output#, State
from dash import html, register_page, get_app, clientside_callback, dcc#, ctx
from dash_tvlwc.types import ColorType, SeriesType
import os
import requests, json
#import sys
#sys.path.append('..')
#import app
import logging
from flask_caching import Cache
from logging.handlers import RotatingFileHandler
from user_agents import parse
#import dash_bootstrap_components as dbc
from flask import session

register_page(__name__,
    title='4.比特币市值偏差',
    name='4.比特币市值偏差')
app1 = get_app()

# 创建FileHandler，并添加到logger.handlers列表
logger = logging.getLogger(__name__)
handler = logging.FileHandler('error.log')
logger.setLevel(logging.INFO)#)DEBUG
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


layout = html.Div([
            #dcc.Interval(id='timer', interval=500),
            dcc.Store(id="store-3"),
            html.Div(className='container', children=[
                html.Div([
                    html.Div([
                        html.Div([
                            dcc.Link("主页", href="/"),
                            html.Br(),
                            dcc.Link("1.钱翻一番历史回测", href="/money-double-strategy-back-test"),
                            html.Br(),
                            dcc.Link("2.比特币因子", href="/bitcoin-factor"),
                            html.Br(),
                            dcc.Link("3.比特币预测市值", href="/bitcoin-predicted-marketcap"),
                            html.Br(),
                            dcc.Link("5.比特币市值上限和下限", href="/bitcoin-upper-lower-marketcap"),
                            html.Br(),
                            dcc.Link("6.比特币价格上限和下限", href="/bitcoin-upper-lower-price"),
                            html.Br(),
                            dcc.Link("7.案例", href="/case")
                        ])
                        #    dcc.Link(f"{page['name']}", href=page["relative_path"])# - {page['path']}
                        #) for page in page_registry.values()
                    ]),            
                ]),
                html.Div(className='main-container', children=[
                    html.H2('比特币市值偏差和市值图 📊'),
                    html.H3('比特币市值和比特币预测市值的差为比特币市值偏差，比特币市值和比特币市值偏差的顶部和底部很一致，而且比特币市值偏差在-1到2之间震荡，比特币市值偏差能预测比特币市值的牛市顶部和熊市底部。'),
                    html.Div(id="main_panel-3")
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
    Output("store-3", "data"),
    Input("store-3", "data"),
)

@app1.callback(Output("main_panel-3", "children"), Input("store-3", "data"))
def update(JSoutput):
    home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'
    def get_token():
        auth_path = '/api/admins/auth-with-password'
        auth_url = home_url + auth_path
        username = os.environ.get('admin_username')
        #print('admin_username: ', username)
        logger.debug('admin_username: {}'.format(username))
        password = os.environ.get('admin_password')
        # json.dumps 将python数据结构转换为JSON
        data1 = json.dumps({"identity": username, "password": password})
        # Content-Type 请求的HTTP内容类型 application/json 将数据已json形式发给服务器
        header1 = {"Content-Type": "application/json"}
        response1 = requests.post(auth_url, data=data1, headers=header1)
        response1_json = response1.json()
        response1_str = str(response1_json)
        #print('html: ', html)
        logger.debug('response1_str: {}'.format(response1_str[0:100]))
        # html.json JSON 响应内容，提取token值
        if response1_json['token']:
            token = response1_json['token']
            session['token'] = token
            logger.debug('save session: {}'.format(session))
            return token
    TIMEOUT = 60 * 60 * 24
    @cache.memoize(timeout=TIMEOUT)
    def get_marketcap_bias3(frequency='weekly'):

        if session.get('token'):
            token = session.get('token')
            #print('token: ', token)
        else:
            token = get_token()
        # 使用已经登录获取到的token 发送一个get请求
        get_path = '/api/collections/bitcoin_trade_signal/records'
        data_marketcap_log = []
        data_blocks_log = []
        if frequency == 'monthly':
            for i in range(1,14):             
                query_predicted_marketcap_log = "?filter=(day_of_month=1)&&fields=date,marketcap_log,marketcap_bias&&perPage=12&&page=" + str(i)#&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
                get_url = home_url + get_path + query_predicted_marketcap_log
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
                    value2 = item['marketcap_bias']
                    logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)))
                    #print('time: ', time, ', value: ', value)
                    data_marketcap_log.append({'time': time, 'value': value1})
                    data_blocks_log.append({'time': time, 'value': value2})
                data = [data_marketcap_log, data_blocks_log]
        elif frequency == 'weekly':
            for i in range(1,14):
                query_predicted_marketcap_log = "?filter=(weekday=1)&&fields=date,marketcap_log,marketcap_bias&&perPage=52&&page=" + str(i)#&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
                get_url = home_url + get_path + query_predicted_marketcap_log
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
                    value2 = item['marketcap_bias']
                    logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)))
                    #print('time: ', time, ', value: ', value)
                    data_marketcap_log.append({'time': time, 'value': value1})
                    data_blocks_log.append({'time': time, 'value': value2})
            data = [data_marketcap_log, data_blocks_log]
        return data
    user_agent = parse(JSoutput)
    is_mobile = user_agent.is_mobile
    is_tablet = user_agent.is_tablet
    is_pc = user_agent.is_pc
    if is_pc:
        data1 = get_marketcap_bias3(frequency='weekly')
    elif is_mobile or is_tablet:
        data1 = get_marketcap_bias3(frequency='monthly') 

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
                            'title': '比特币市值偏差',
                            'color': 'orange' 
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


