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
from dash.exceptions import PreventUpdate

register_page(__name__,
    title='7.我的分享',
    name='7.我的分享-客户')
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
            dcc.Store(id="store_12"),            
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
                            dcc.Link("5.比特币价格上限和下限", href="/bitcoin-upper-lower-price-client"),
                            html.Br(),
                            dcc.Link("6.我的累计收益率", href="/my-total-return-client")
                        ])
                        #    dcc.Link(f"{page['name']}", href=page["relative_path"])# - {page['path']}
                        #) for page in page_registry.values()
                    ]),            
                ]),
                html.Br(),
                html.Div([
                    dcc.Input(id="input1",
                        type="text",
                        placeholder="公开的昵称"), 
                    html.Div([html.Img(id='output-image-database', style={'width': '50px', 'height': '50px'})],style={'padding': 10, 'flex': 1}),
                    dcc.Upload(
                        id='upload-image',
                        children=html.Div([
                            '拖拽文件或',
                            html.A(' 点击上传')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                    ),
                    html.Div([html.Img(id='output-image-upload', style={'width': '50px', 'height': '50px'})],style={'padding': 10, 'flex': 1}),
                ]),
                dcc.RadioItems(['不公开', '公开'],  id="radio_items"),
                html.Br(),
               ## button
                html.Button('  提交  ', id='button_12', n_clicks=0),
                html.Div(id="nick_name"),
                html.Div(id="grid_container2"),#[grid]
                html.Div(id="main_panel-12"),
 
                #html.Span('李力, 2024')
            ])
        ]
    )

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
    Output("store_12", "data"),
    Input("store_12", "data"),
)

@app1.callback(
    Output("input1", "value"),
    Output("output-image-database", "src"),
    Output("radio_items", "value"),
    Input('url', 'pathname'))
def update_input(pathname):
    def get_client_id():
        if session.get('token'):
            token = session.get('token')
            #print('token: ', token)
            username = session.get('username')
            #print('username: ', username)
            home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'
            # 使用已经登录获取到的token，查询client_id
            get_path = '/api/collections/clients/records'

            query_client_id = "?filter=(username='" + username + "'||email='" + username + "')&&fields=id"#&&page=50&&perPage=100&&date&&skipTotal=1response1_json
            get_url = home_url + get_path + query_client_id
            header = {
                "Content-Type": "application/json",
                "Authorization": token
            }
            response = requests.get(get_url, headers=header)
            response_json = response.json()
            response_str = str(response_json)
            logger.debug('response_str: {}'.format(response_str[0:100]))
            #print('response_str: {}'.format(response_str[0:100]))
            client_id = response_json['items'][0]['id']
        return client_id
    client_id = get_client_id()
    home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'

    if session.get('token'):
        token = session.get('token')
        logger.debug('token: {}'.format(token))
        # 使用已经登录获取到的token 发送一个get请求
        get_path = '/api/collections/clients/records'

        query_field1 = "?filter=(id='" + client_id + "')&&fields=field1,field2,field4&&perPage=1&&page=1"# + str(i)&&page=50&&perPage=100&&sort=date&&skipTotal=1response1_json
        get_url = home_url + get_path + query_field1
        header2 = {
            "Content-Type": "application/json",
            "Authorization": token
        }
        response4 = requests.get(get_url, headers=header2)
        response4_json = response4.json()
        response4_str = str(response4_json)
        logger.debug('response4_str: {}'.format(response4_str[0:100]))
        if response4_json['totalItems'] > 0:
            field1 = response4_json['items'][0]['field1']
            field2 = response4_json['items'][0]['field2']
            field4 = response4_json['items'][0]['field4']
            logger.debug('field1: {}, field4: {}'.format(field1, field4))
            if field4 == True:
                get_radio_items = "公开"
            else:
                get_radio_items = "不公开"
    return field1, field2, get_radio_items   

@app1.callback(
    Output("output-image-upload", "src"),
    Input("upload-image", "contents"),
)
def update_output_image(list_of_contents):
    if list_of_contents is not None:
        logger.debug('list_of_contents: {}'.format(list_of_contents[0:10]))
    return list_of_contents
@app1.callback(
        Output("nick_name", "children"),
        Output("grid_container2", "children"),
        Output("main_panel-12", "children"),
        Input("output-image-upload", "src"),
        Input("output-image-database", "src"),
        Input("radio_items", "value"),
        Input("input1", "value"),
        Input("store_12", "data")
    )
def update_my_share(upload_contents, database_contents, radio_items, input1, store_12):

    if radio_items == '公开':
        contents = ""
        if upload_contents is not None:
            logger.debug('upload_contents: {}'.format(upload_contents[0:10]))
            contents = upload_contents
        elif database_contents is not None:
            logger.debug('database_contents: {}'.format(database_contents[0:10]))
            contents = database_contents
        logger.debug('contents: {}'.format(contents[0:10]))

        nick_name = html.Div([
            html.Div([html.Img(src=contents, style={'width': '50px', 'height': '50px'})],style={'padding': 10, 'flex': 1}),
            html.Div([html.H3(input1)], style={'padding': 10, 'flex': 1}),
            html.Div("    ",style={'padding': 10, 'flex': 1}),
            html.Div("    ",style={'padding': 10, 'flex': 1}),
            html.Div("    ",style={'padding': 10, 'flex': 1}),
            #html.Div("    ",style={'padding': 10, 'flex': 1}),
            #html.Div("    ",style={'padding': 10, 'flex': 1}),
            #html.Div("    ",style={'padding': 10, 'flex': 1}),
            #html.Div("    ",style={'padding': 10, 'flex': 1}),
            #html.Div("    ",style={'padding': 10, 'flex': 1}),
            #html.Div("    ",style={'padding': 10, 'flex': 1}),
            #html.Div("    ",style={'padding': 10, 'flex': 1}),
            #html.Div("    ",style={'padding': 10, 'flex': 1}),
            #html.Div("    ",style={'padding': 10, 'flex': 1}),
        ], style={'display': 'flex', 'flexDirection': 'row'})
        TIMEOUT = 60 * 60 * 24
        def get_client_id():
            if session.get('token'):
                token = session.get('token')
                #print('token: ', token)
                username = session.get('username')
                #print('username: ', username)
                home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'
                # 使用已经登录获取到的token，查询client_id
                get_path = '/api/collections/clients/records'

                query_client_id = "?filter=(username='" + username + "'||email='" + username + "')&&fields=id"#&&page=50&&perPage=100&&date&&skipTotal=1response1_json
                get_url = home_url + get_path + query_client_id
                header = {
                    "Content-Type": "application/json",
                    "Authorization": token
                }
                response = requests.get(get_url, headers=header)
                response_json = response.json()
                response_str = str(response_json)
                logger.debug('response_str: {}'.format(response_str[0:100]))
                #print('response_str: {}'.format(response_str[0:100]))
                client_id = response_json['items'][0]['id']
            return client_id
        client_id = get_client_id() 
        @cache.memoize(timeout=TIMEOUT)
        def get_my_total_return_client2(frequency = 'daily',client_id=''):
            home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'

            if session.get('token'):
                token = session.get('token')
                logger.debug('token: {}'.format(token))
                # 使用已经登录获取到的token 发送一个get请求
                get_path = '/api/collections/clients_trade_account/records'
                data_total_return = []
                data_annualized_return = {'time': '', 'annualized_return': 0, 'annualized_volatility': 0,
                                                    'annualized_sharpe': 0, 'max_drawdown': 0}
                if frequency == 'daily':
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
                        if response2_json['totalItems'] > 0:
                            for item in response2_json['items']:
                                time = item['date']
                                value1 = item['total_return'] * 100
                                #app1.logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)) + ' ,value3:{}'.format(str(value3)))
                                #print('time: ', time, ', value: ', value)
                                data_total_return.append({'time': time, 'value': value1})
                        else:
                            data_total_return.append({'time': 0, 'value': 0})
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
                    if response3_json['totalItems'] > 0:
                        data_annualized_return['time'] = response3_json['items'][0]['date'][0:10]
                        data_annualized_return['annualized_return'] = response3_json['items'][0]['annualized_return'] * 100
                        data_annualized_return['annualized_volatility'] = response3_json['items'][0]['annualized_volatility'] * 100
                        data_annualized_return['annualized_sharpe'] = response3_json['items'][0]['annualized_sharpe']
                        data_annualized_return['max_drawdown'] = response3_json['items'][0]['max_drawdown'] * 100
                        #app1.logger.debug('time: {}'.format(str(time)) + ' ,value1:{}'.format(str(value1)) + ' ,value2:{}'.format(str(value2)) + ' ,value3:{}'.format(str(value3)))
                        #print('time: ', time, ', value: ', value)
                    else:
                        data_annualized_return['time'] = 0
                        data_annualized_return['annualized_return'] = 0
                        data_annualized_return['annualized_volatility'] = 0
                        data_annualized_return['annualized_sharpe'] = 0
                        data_annualized_return['max_drawdown'] = 0
                data = [data_total_return, data_annualized_return]
            else:
                data = [generate_random_series(5000, n=500), generate_random_series(5000, n=500)]

            return data
    
        data0 = get_my_total_return_client2(frequency='daily',client_id=client_id)
        data_annualized_return = data0[1]
        #df1 = pd.DataFrame(data_annualized_return)
        #df2_1 = df1[['annualized_return ', 'annualized_volatility']]
        #df2_2 = df1[['annualized_sharpe ', 'max_drawdown']]

        columnDefs1 = [
            { 'field': 'time', 'headerName': '日期' },
            { 'field': 'annualized_return', 'headerName': '年化收益率%'},
            { 'field': 'annualized_volatility', 'headerName': '年化波动率%'},
            { 'field': 'annualized_sharpe', 'headerName': '年化夏普比率'},
            { 'field': 'max_drawdown', 'headerName': '最大回撤比率%'},
        ]
        columnDefs2_1 = [
            { 'field': 'annualized_return', 'headerName': '年化收益率%'},
            { 'field': 'annualized_volatility', 'headerName': '年化波动率%'},
        ]
        columnDefs2_2 = [
            { 'field': 'annualized_sharpe', 'headerName': '年化夏普比率'},
            { 'field': 'max_drawdown', 'headerName': '最大回撤比率%'},
        ]

        grid1 = dag.AgGrid(
            id="grid1",
            #rowData=df1.to_dict("records"),
            rowData=[data_annualized_return],
            columnDefs=columnDefs1,
            style={'height': '100px', 'width': '100%'},
            columnSize="sizeToFit"
        )
        grid2_1 = dag.AgGrid(
            id="grid2_1",
            rowData=[data_annualized_return],
            columnDefs=columnDefs2_1,
            style={'height': '100px', 'width': '100%'},
            columnSize="sizeToFit"
        )
        grid2_2 = dag.AgGrid(
            id="grid2_2",
            rowData=[data_annualized_return],
            columnDefs=columnDefs2_2,
            style={'height': '100px', 'width': '100%'},
            columnSize="sizeToFit"
        )
        logger.debug('data0[0]: {}'.format(str(data0[0])[0:50]))
        logger.debug('data0[1]: {}'.format(str(data0[1])[0:50]))

        main_panel = [
            html.H2('我的累计收益率图 📊'),
            #html.H3('根据历史经验，比特币市值偏差为1时，比特币市值在牛市顶部，计算出的比特币价格为牛市的价格上限，比特币市值偏差为-0.95时，比特币市值在熊市底部，计算出的比特币价格为熊市的价格下限。'),

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
        user_agent = parse(store_12)
        is_mobile = user_agent.is_mobile
        is_tablet = user_agent.is_tablet
        is_pc = user_agent.is_pc
        if is_pc:
            return nick_name, [grid1], main_panel
        elif is_mobile or is_tablet:
            return nick_name, [grid2_1, grid2_2], main_panel
    else:
        nick_name = ''
        grid1 = ''
        main_panel = ''
        return nick_name, [grid1], main_panel
    
@app1.callback(
        Input("output-image-upload", "src"),
        Input("output-image-database", "src"),
        Input("radio_items", "value"),
        Input("input1", "value"),
        Input("button_12", "n_clicks"),
)
def update_database(upload_contents, database_contents, radio_items, input1, n_clicks):
    def get_client_id():
        if session.get('token'):
            token = session.get('token')
            #print('token: ', token)
            username = session.get('username')
            #print('username: ', username)
            home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'
            # 使用已经登录获取到的token，查询client_id
            get_path = '/api/collections/clients/records'

            query_client_id = "?filter=(username='" + username + "'||email='" + username + "')&&fields=id"#&&page=50&&perPage=100&&date&&skipTotal=1response1_json
            get_url = home_url + get_path + query_client_id
            header = {
                "Content-Type": "application/json",
                "Authorization": token
            }
            response = requests.get(get_url, headers=header)
            response_json = response.json()
            response_str = str(response_json)
            logger.debug('response_str: {}'.format(response_str[0:100]))
            #print('response_str: {}'.format(response_str[0:100]))
            client_id = response_json['items'][0]['id']
        return client_id
    client_id = get_client_id() 
    if n_clicks > 0:
        contents = ""
        if upload_contents is not None:
            logger.debug('upload_contents: {}'.format(upload_contents[0:10]))
            contents = upload_contents
        elif database_contents is not None:
            logger.debug('database_contents: {}'.format(database_contents[0:10]))
            contents = database_contents
        logger.debug('contents: {}'.format(contents[0:10]))            
        if radio_items  == "公开":
            is_open = True
        else:
            is_open = False
        if session.get('token'):
            token = session.get('token')
            #print('token: ', token)
            home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'
            # 使用已经登录获取到的token，发送数据
            patch_path = '/api/collections/clients/records/' + client_id
            data = {
                'field1':input1,
                'field2': contents,
                'field4': is_open,
            }
            data_json = json.dumps(data)
            patch_url = home_url + patch_path
            header = {
                "Content-Type": "application/json",
                "Authorization": token
            }
            response = requests.patch(patch_url, headers=header, data=data_json)
            response_json = response.json()
            response_str = str(response_json)
            if response.status_code == 200:
                logger.debug('client_id: {}, post successful.'.format(client_id))
            else:
                logger.debug('response_str: {}'.format(response_str[0:100]))
            #print('response_str: {}'.format(response_str[0:100]))