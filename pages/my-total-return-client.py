#import random
#from datetime import datetime, timedelta
from data_generator import generate_random_series
import dash_tvlwc
#import dash
from dash.dependencies import Input, Output
from dash import html, register_page, get_app, dcc, clientside_callback#, ctx
from dash_tvlwc.types import ColorType, SeriesType
import os
import requests, json
#import sys
#sys.path.append('..')
import logging
from flask_caching import Cache
from logging.handlers import RotatingFileHandler
#import dash_bootstrap_components as dbc
from user_agents import parse
from flask_login import current_user
from utils.login_handler import require_login
from flask import session
import pandas as pd
import dash_ag_grid as dag

register_page(__name__,
    title='6.我的总回报',
    name='6.我的总回报-客户')
require_login(__name__)
app1 = get_app()
# 创建logger
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
        return html.Div(["请 ", dcc.Link("登录", href="/login"), " 继续查看。"])

    return html.Div(
        [
            #dcc.Interval(id='timer', interval=500),
            dcc.Store(id="store-11"),            
            html.Div(className='container', children=[
                html.Div([
                    html.Div([
                        html.Div([
                            dcc.Link("主页", href="/home-client"),
                            html.Br(),
                            dcc.Link("1.比特币因子", href="/bitcoin-factor-client"),
                            html.Br(),
                            dcc.Link("2.比特币预测市值", href="/bitcoin-predicted-marketcap-client"),
                            html.Br(),
                            dcc.Link("3.比特币市值偏离度", href="/bitcoin-marketcap-bias-client"),
                            html.Br(),
                            dcc.Link("4.比特币市值上限和下限", href="/bitcoin-upper-lower-marketcap-client"),
                            html.Br(),
                            dcc.Link("5.比特币价格上限和下限", href="/bitcoin-upper-lower-price-client")
                        ])
                        #    dcc.Link(f"{page['name']}", href=page["relative_path"])# - {page['path']}
                        #) for page in page_registry.values()
                    ]),            
                ]),
                # show annualized_return,annualized_volatility,annualized_sharpe,max_drawdown values
                html.Div(id="grid_container"),#[grid]
                html.Div(className='main-container', children=[
                    html.H2('我的累计收益率图 📊'),
                    #html.H3('根据历史经验，比特币市值偏差为1时，比特币市值在牛市顶部，计算出的比特币价格为牛市的价格上限，比特币市值偏差为-0.95时，比特币市值在熊市底部，计算出的比特币价格为熊市的价格下限。'),
                    html.Div(id="main_panel-11")
                ]),
                #html.Span('李力, 2024')
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
    Output("store-11", "data"),
    Input("store-11", "data"),
)

@app1.callback(
        Output("grid_container", "children"),
        Output("main_panel-11", "children"),
        Input("store-11", "data"))
def update(JSoutput):
    TIMEOUT = 60 * 60 * 24
    @cache.memoize(timeout=TIMEOUT)
    def get_my_total_return_client1(frequency = 'daily'):
        home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'
        '''
        auth_path = '/api/admins/auth-with-password'
        auth_url = home_url + auth_path
        username = os.environ.get('admin_username')
        #print('username: ', username)
        password = os.environ.get('admin_password')
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
        '''
        if session.get('token'):
            token = session.get('token')
            logger.debug('token: {}'.format(token))
            username = session.get('username')
            logger.debug('username: {}'.format(username))
            # 使用已经登录获取到的token 发送一个get请求
            get_path = '/api/collections/clients_trade_account/records'
            data_total_return = []
            data_annualized_return = {'time': [], 'annualized_return': [], 'annualized_volatility': [],
                                                'annualized_sharpe': [], 'max_drawdown': []}
            if frequency == 'daily':
                # 使用已经登录获取到的token，查询client_id
                get_path0 = '/api/collections/clients/records'

                query_client_id = "?filter=(username='" + username + "'||email='" + username + "')&&fields=id"#&&page=50&&perPage=100&&date&&skipTotal=1response1_json
                get_url0 = home_url + get_path0 + query_client_id
                header = {
                    "Content-Type": "application/json",
                    "Authorization": token
                }
                response = requests.get(get_url0, headers=header)
                response_json = response.json()
                response_str = str(response_json)
                logger.debug('response_str: {}'.format(response_str[0:100]))
                #print('response_str: {}'.format(response_str[0:100]))
                client_id = response_json['items'][0]['id']
                for i in range(1,2):
                    get_path = '/api/collections/clients_trade_account/records'

                    query_total_return = "?filter=(client_id='" + client_id + "')&&fields=date,total_return&&perPage=365&&page=" + str(i)#&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
                    get_url = home_url + get_path + query_total_return
                    header2 = {
                        "Content-Type": "application/json",
                        "Authorization": token
                    }
                    response2 = requests.get(get_url, headers=header2)
                    response2_json = response2.json()
                    response2_str = str(response2_json)
                    logger.debug('response2_str: {}'.format(response2_str[0:100]))
                    for item in response2_json['items']:
                        time = item['date']
                        value1 = item['total_return'] * 100
                        #app1.logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)) + ' ,value3:{}'.format(str(value3)))
                        #print('time: ', time, ', value: ', value)
                        data_total_return.append({'time': time, 'value': value1})

                query_annualized_return = "?filter=(client_id='" + client_id + "')&&fields=date,annualized_return,annualized_volatility,annualized_sharpe,max_drawdown&&sort=-date&&perPage=1&&page=1"# + str(i)&&page=50&&perPage=100&&skipTotal=1response1_json
                get_url2 = home_url + get_path + query_annualized_return
                header2 = {
                    "Content-Type": "application/json",
                    "Authorization": token
                }
                response3 = requests.get(get_url2, headers=header2)
                response3_json = response3.json()
                response3_str = str(response3_json)
                logger.debug('response2_str: {}'.format(response3_str[0:100]))
                data_annualized_return['time'].append(response3_json['items'][0]['date'])
                data_annualized_return['annualized_return'].append(response3_json['items'][0]['annualized_return'] * 100)
                data_annualized_return['annualized_volatility'].append(response3_json['items'][0]['annualized_volatility'] * 100)
                data_annualized_return['annualized_sharpe'].append(response3_json['items'][0]['annualized_sharpe'])
                data_annualized_return['max_drawdown'].append(response3_json['items'][0]['max_drawdown'] * 100)
                #app1.logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)) + ' ,value3:{}'.format(str(value3)))
                #print('time: ', time, ', value: ', value)
            data = [data_total_return, data_annualized_return]
        else:
            data = [generate_random_series(5000, n=500), generate_random_series(5000, n=500)]

        return data
    data0 = get_my_total_return_client1(frequency='daily')
    data_annualized_return = data0[1]
    df = pd.DataFrame(data_annualized_return)
    columnDefs = [
        { 'field': 'time', 'headerName': '日期' },
        { 'field': 'annualized_return', 'headerName': '年化收益率%'},
        { 'field': 'annualized_volatility', 'headerName': '年化波动率%'},
        { 'field': 'annualized_sharpe', 'headerName': '年化夏普比率'},
        { 'field': 'max_drawdown', 'headerName': '最大回撤比率%'},
    ]

    grid = dag.AgGrid(
        id="getting-started-headers",
        rowData=df.to_dict("records"),
        columnDefs=columnDefs,
        style={'height': '100px', 'width': '100%'}
    )
    '''
    user_agent = parse(JSoutput)
    is_mobile = user_agent.is_mobile
    is_tablet = user_agent.is_tablet
    is_pc = user_agent.is_pc
  
    if is_pc:
        data1 = get_my_total_return_client(frequency='daily')
    elif is_mobile or is_tablet:
        data1 = get_my_total_return_client(frequency='daily') 
    #data1 = get_upper_lower_marketcap(frequency = 'weekly')
    '''
    logger.debug('data0[0]: {}'.format(str(data0[0])[0:10]))
    logger.debug('data0[1]: {}'.format(str(data0[1])[0:10]))

    main_panel = [
        html.Div(style={'position': 'relative', 'width': '100%', 'height': '100%', 'marginBottom': '30px'}, children=[
            html.Div(children=[
                dash_tvlwc.Tvlwc(
                    #id='tv-chart-1',
                    #seriesData=[generate_random_ohlc(1000, n=1000)],
                    #seriesTypes=[SeriesType.Candlestick],
                    seriesData=[data0[0]],
                    seriesTypes=[SeriesType.Line],
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
                            'priceFormatter': "(function(price) { return '%' + price.toFixed(2); })"
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
                            'title': '我的累计收益率',
                            #'color': 'blue' 
                            #'priceScaleId': 'left'
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
    return [grid], main_panel