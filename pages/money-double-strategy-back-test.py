#import random
#from datetime import datetime, timedelta
#from data_generator import generate_random_series
import dash_tvlwc
#import dash
from dash.dependencies import Input, Output#, State
from dash import html, clientside_callback, dcc, register_page, get_app#, ctx

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
from flask import session
from dash import dash_table

register_page(__name__,
    title='1.钱翻一番历史回测',
    name='1.钱翻一番历史回测')
app1 = get_app()

# 创建FileHandler，并添加到logger.handlers列表
logger = logging.getLogger(__name__)
handler = logging.FileHandler('error.log')
logger.setLevel(logging.INFO)#)  DEBUG
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
            dcc.Store(id="store-13"),
            html.Div(className='container', children=[
                html.Div([
                    html.Div([
                        html.Div([
                            dcc.Link("主页", href="/"),
                            html.Br(),
                            dcc.Link("2.比特币因子", href="/bitcoin-factor"),
                            html.Br(),
                            dcc.Link("3.比特币预测市值", href="/bitcoin-predicted-marketcap"),
                            html.Br(),
                            dcc.Link("4.比特币市值偏差", href="/bitcoin-marketcap-bias"),
                            html.Br(),
                            dcc.Link("5.比特币市值上限和下限", href="/bitcoin-upper-lower-marketcap"),
                            html.Br(),
                            dcc.Link("6.比特币价格上限和下限", href="/bitcoin-upper-lower-price"),
                            html.Br(),
                            #dcc.Link("7.案例", href="/case")
                        ])
                        #    dcc.Link(f"{page['name']}", href=page["relative_path"])# - {page['path']}
                        #) for page in page_registry.values()
                    ]),            
                ]),
                html.Div(className='main-container', children=[
                    html.H2('钱翻一番策略历史回测业绩图 📊'),
                    html.H3('钱翻一番策略在过去9年历史回测中，实现了年化收益率134%，年化波动率49%，最大回撤比率32%的好成绩。'),
                    html.Div(id="main_panel-13")
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
    Output("store-13", "data"),
    Input("store-13", "data"),
)

@app1.callback(Output("main_panel-13", "children"), Input("store-13", "data"))
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
    def get_fanyifan_back_test(frequency='monthly'):

        if session.get('token'):
            token = session.get('token')
            #print('token: ', token)
        else:
            token = get_token()
        # 使用已经登录获取到的token 发送一个get请求
        get_path = '/api/collections/bitcoin_strategy_backtest_returns/records'
        data_cum_returns = []
        data_portfolio_value = []
        if frequency == 'monthly':
            for i in range(1, 10):        
                query_cum_returns = "?fields=date,portfolio_value,cum_return&&perPage=365&&page=" + str(i)#&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
                get_url = home_url + get_path + query_cum_returns
                header2 = {
                    "Content-Type": "application/json",
                    "Authorization": token
                }
                response2 = requests.get(get_url, headers=header2)
                response2_json = response2.json()
                response2_str = str(response2_json)
                #logger.debug('response2_str: {}'.format(response2_str))
                for item in response2_json['items']:
                    time = item['date']
                    value1 = item['portfolio_value'] / 1000000
                    value2 = item['cum_return']
                    #logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)))
                    #print('time: ', time, ', value: ', value)
                    data_portfolio_value.append({'time': time, 'value': value1})
                    data_cum_returns.append({'time': time, 'value': value2})
        # 使用已经登录获取到的token 发送一个get请求
        get_path3 = '/api/collections/bitcoin_strategy_backtest_cn_stock_performance/records'
        data_performance = {'instrument': '', 'instrument_annual_return': '', 'instrument_annual_volatility': '', 'instrument_sharpe': ''}
        query_performance = "?filter=(instrument='BTCUSD')&&fields=instrument,instrument_annual_return,instrument_annual_volatility,instrument_sharpe&&perPage=1&&page=1"# + str(i)&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
        get_url3 = home_url + get_path3 + query_performance
        header3 = {
            "Content-Type": "application/json",
            "Authorization": token
        }
        response3 = requests.get(get_url3, headers=header3)
        response3_json = response3.json()
        response3_str = str(response3_json)
        logger.debug('response3_str: {}'.format(response3_str))
        for item in response3_json['items']:
            data_performance['instrument'] = item['instrument']
            data_performance['instrument_annual_return'] = item['instrument_annual_return'] * 100
            data_performance['instrument_annual_volatility'] = round(item['instrument_annual_volatility'] * 100, 2)
            data_performance['instrument_sharpe'] = item['instrument_sharpe']
          
        data = [data_performance, data_portfolio_value, data_cum_returns]
        '''
        elif frequency == 'weekly':
            for i in range(1,14):
                query_bitcoin_marketcap_log = "?filter=(weekday=1)&&fields=date,marketcap_log,blocks_log&&perPage=52&&page=" + str(i)#&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
                get_url = home_url + get_path + query_bitcoin_marketcap_log
                header2 = {
                    "Content-Type": "application/json",
                    "Authorization": token
                }
                response2 = requests.get(get_url, headers=header2)
                response2_json = response2.json()
                response2_str = str(response2_json)
                #logger.debug('response2_str: {}'.format(response2_str))
                for item in response2_json['items']:
                    time = item['date']
                    value1 = item['marketcap_log']
                    value2 = item['blocks_log']
                    #logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)))
                    #print('time: ', time, ', value: ', value)
                    data_marketcap_log.append({'time': time, 'value': value1})
                    data_blocks_log.append({'time': time, 'value': value2})
            data = [data_marketcap_log, data_blocks_log]
        '''
        return data
    user_agent = parse(JSoutput)
    is_mobile = user_agent.is_mobile
    is_tablet = user_agent.is_tablet
    is_pc = user_agent.is_pc
    if is_pc:
        data1 = get_fanyifan_back_test(frequency='monthly')
    elif is_mobile or is_tablet:
        data1 = get_fanyifan_back_test(frequency='monthly') 
    back_test_list = []
    columnDefs1 = [
        {'name': '交易品种', 'id': 'instrument'},
        {'name': '年化收益率%', 'id': 'instrument_annual_return'},
        {'name': '年化波动率%', 'id': 'instrument_annual_volatility'},
        {'name': '年化夏普比率', 'id': 'instrument_sharpe'},
    ]

    grid1 = dash_table.DataTable(
        id="grid1",
        columns=[{"name": i['name'], "id": i['id']} for i in columnDefs1],
        data=[data1[0]],
        style_table={'height': '100px', 'width': '100%'},
        style_cell={'textAlign': 'center'}
    )
    logger.debug('data1[0]: {}'.format(str(data1[0])))
    #logger.debug('data1[1]: {}'.format(str(data1[1])[0:10]))
    main_panel = [
        html.Div(style={'position': 'relative', 'width': '100%', 'height': '100%', 'marginBottom': '30px'}, children=[
            html.Div(children=[
                dash_tvlwc.Tvlwc(
                    #id='tv-chart-1',
                    #seriesData=[generate_random_ohlc(1000, n=1000)],
                    #seriesTypes=[SeriesType.Candlestick],
                    seriesData=[data1[1], data1[2]],
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
                            #'priceFormatter': "(function(price) { return price.toFixed(0) ; })"
                            #+  + '$'
                        },
                        'rightPriceScale': {
                            'visible': 'true',
                            'priceFormatter': "(function(price) { return (price).toFixed(0); })"  # 右轴价格格式化

                        },
                        'leftPriceScale': {
                            'visible': 'true',
                            'priceFormatter': "(function(price) { return (price / 1000000).toFixed(0) + 'M$'; })"  # 左轴价格格式化

                        }
                    },
                    seriesOptions=[
                        {
                            'title': '模拟账户价值-百万美元',
                            'color': '#B2DFF7',
                            'priceScaleId': 'left'
                        },
                        {
                            'title': '模拟账户累计收益率',
                            'color': '#B2E0D9', 
                            'priceScaleId': 'right'
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
    back_test_list.append(html.Div(grid1))
    back_test_list.append(html.Div(main_panel))    
    return back_test_list if back_test_list else html.Div("没有找到回测数据")