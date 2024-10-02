#import dash
from dash import html, register_page, get_app, dcc, Input, Output
import dash_daq as daq
import requests, json
import logging
from flask_caching import Cache
#from logging.handlers import RotatingFileHandler
import os
#import dash_bootstrap_components as dbc
from flask import session


register_page(__name__, 
    path='/',
    title='钱翻一番-主页',
    name='主页')
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
    html.Div([
        html.Div([
            html.Div([
                dcc.Link("主页", href="/"),
                html.Br(),
                dcc.Link("1.比特币因子", href="/bitcoin-factor"),
                html.Br(),
                dcc.Link("2.比特币预测市值", href="/bitcoin-predicted-marketcap"),
                html.Br(),
                dcc.Link("3.比特币市值偏差", href="/bitcoin-marketcap-bias"),
                html.Br(),
                dcc.Link("4.比特币市值上限和下限", href="/bitcoin-upper-lower-marketcap"),
                html.Br(),
                dcc.Link("5.比特币价格上限和下限", href="/bitcoin-upper-lower-price"),
                html.Br(),
                dcc.Link("6.案例", href="/case")
        ])
            #    dcc.Link(f"{page['name']}", href=page["relative_path"])# - {page['path']}
            #) for page in page_registry.values()
        ]),            
    ]),
    html.Div(id='gauge-container')  
])

@app1.callback(Output('gauge-container', 'children'),
              Input('url', 'pathname')
              )
def update_gauge_output(pathname):
    home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'
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
    TIMEOUT = 60 * 60 * 24
    @cache.memoize(timeout=TIMEOUT)
    def get_upper_lower_price():
        if token:
            # 使用已经登录获取到的token 发送一个get请求
            get_path = '/api/collections/bitcoin_trade_signal/records'

            query_predicted_marketcap_log = "?fields=date,price,price_lower_limit,price_upper_limit,predicted_price&&sort=-created&&perPage=1&&page=365"#&&page=50&&perPage=100&&date&&skipTotal=1response1_json
            get_url = home_url + get_path + query_predicted_marketcap_log
            header2 = {
                "Content-Type": "application/json",
                "Authorization": token
            }
            response2 = requests.get(get_url, headers=header2)
            response2_json = response2.json()
            response2_str = str(response2_json)
            logger.debug('response2_str: {}'.format(response2_str[0:100]))
        
            time = response2_json['items'][-1]['date'][0:10]
            data_price = response2_json['items'][-1]['price']
            data_price_lower_limit = response2_json['items'][-1]['price_lower_limit']
            data_price_upper_limit = response2_json['items'][-1]['price_upper_limit']
            data_predicted_price = response2_json['items'][-1]['predicted_price']
            #app1.logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)) + ' ,value3:{}'.format(str(value3)))
            #print('time: ', time, ', value: ', value)

                
            data = [time, data_price, data_price_lower_limit, data_price_upper_limit, data_predicted_price]
        else:
            data = ["2024-07-22", 39877, 229876, 325477, 35741]

        return data

    if pathname == '/':
        data1 = get_upper_lower_price()
        logger.debug('data1[0]: {}'.format(str(data1[0])[0:10]))
        logger.debug('data1[1]: {}'.format(str(data1[1])[0:10]))
        logger.debug('data1[2]: {}'.format(str(data1[2])[0:10]))
        logger.debug('data1[3]: {}'.format(str(data1[3])[0:10]))
        logger.debug('data1[4]: {}'.format(str(data1[4])[0:10]))
    return html.Div([
    html.H2('一年前数据-' + data1[0],
        style={
            'textAlign': 'center'
        }          
    ),
    html.Div(className='row', children=[
        daq.Gauge(
            value=data1[1]/10000,
            label='比特币价格',
            max=round(data1[3]/10000, 4),
            min=0,
            showCurrentValue=True,
            units="万美元",
            scale={'interval': 2, 'labelInterval': 2}
        ),
        daq.Gauge(
            value=data1[4]/10000,
            label='比特币预测价格',
            max=round(data1[3]/10000, 4),
            min=0,
            showCurrentValue=True,
            units="万美元",
            scale={'interval': 2, 'labelInterval': 2}
        ),
        daq.Gauge(
            value=data1[3]/10000,
            label='比特币价格上限',
            max=round(data1[3]/10000, 4),
            min=0,
            showCurrentValue=True,
            units="万美元",
            scale={'interval': 2, 'labelInterval': 2}
        ) 
    ]) 
    ])