import logging
from urllib.parse import urlparse, parse_qs
import dash
from dash import html, dcc, dash_table
import pandas as pd

# 假设其他导入已经正确完成
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# 初始化日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 假设其他必要的函数和变量已经定义
def get_my_total_return_client3(frequency, client_id):
    # 假设这个函数已经正确实现
    pass

def parse(store_13):
    # 假设这个函数已经正确实现
    pass

def process_client_info(row, nick_name, client_info_list):
    # 获取链接中的客户ID参数
    url_params = urlparse(dash.ctx.request.url)
    query_params = parse_qs(url_params.query)
    client_id_from_url = query_params.get('client_id', None)

    # 如果链接中有客户ID参数，则仅展示该客户的详细信息
    if client_id_from_url and str(client_id_from_url[0]) == str(row['client_id']):
        data0 = get_my_total_return_client3(frequency='daily', client_id=row['client_id'])
        data_annualized_return = data0[1]

        # 确保data_annualized_return是DataFrame或字典格式
        if isinstance(data_annualized_return, dict):
            data_annualized_return = pd.DataFrame([data_annualized_return])

        columnDefs1 = [
            {'field': 'time', 'headerName': '日期'},
            {'field': 'annualized_return', 'headerName': '年化收益率%'},
            {'field': 'annualized_volatility', 'headerName': '年化波动率%'},
            {'field': 'annualized_sharpe', 'headerName': '年化夏普比率'},
            {'field': 'max_drawdown', 'headerName': '最大回撤比率%'},
        ]
        columnDefs2_1 = [
            {'field': 'annualized_return', 'headerName': '年化收益率%'},
            {'field': 'annualized_volatility', 'headerName': '年化波动率%'},
        ]
        columnDefs2_2 = [
            {'field': 'annualized_sharpe', 'headerName': '年化夏普比率'},
            {'field': 'max_drawdown', 'headerName': '最大回撤比率%'},
        ]

        grid1 = dash_table.DataTable(
            id="grid1",
            columns=columnDefs1,
            data=data_annualized_return.to_dict("records"),
            style_table={'height': '100px', 'width': '100%'},
            style_cell={'textAlign': 'center'}
        )
        grid2_1 = dash_table.DataTable(
            id="grid2_1",
            columns=columnDefs2_1,
            data=data_annualized_return.to_dict("records"),
            style_table={'height': '100px', 'width': '100%'},
            style_cell={'textAlign': 'center'}
        )
        grid2_2 = dash_table.DataTable(
            id="grid2_2",
            columns=columnDefs2_2,
            data=data_annualized_return.to_dict("records"),
            style_table={'height': '100px', 'width': '100%'},
            style_cell={'textAlign': 'center'}
        )

        logger.debug('data0[0]: {}'.format(str(data0[0])[0:50]))
        logger.debug('data0[1]: {}'.format(str(data0[1])[0:50]))

        main_panel = [
            html.Div(style={'position': 'relative', 'width': '100%', 'height': '100%', 'marginBottom': '30px'}, children=[
                html.Div(children=[
                    dash_tvlwc.Tvlwc(
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
                                'priceFormatter': "(function(price) { return '%' + price.toFixed(2); })"
                            },
                            'seriesOptions': [
                                {
                                    'title': '累计收益率',
                                }
                            ]
                        },
                    ),
                ], style={'width': '100%', 'height': '100%', 'left': 0, 'top': 0}),
                html.Div(id='chart-info', children=[
                    html.Span(id='chart-price', style={'fontSize': '60px', 'fontWeight': 'bold'}),
                    html.Span(id='chart-date', style={'fontSize': 'small'}),
                ], style={'position': 'absolute', 'left': 0, 'top': 0, 'zIndex': 10, 'color': 'white', 'padding': '10px'})
            ])
        ]

        user_agent = parse(store_13)
        is_mobile = user_agent.is_mobile
        is_tablet = user_agent.is_tablet
        is_pc = user_agent.is_pc

        if is_pc:
            client_info_list.append(html.Div(nick_name))
            client_info_list.append(html.Div([grid1]))
            client_info_list.append(html.Div(main_panel))
            client_info_list.append(html.Hr())

        elif is_mobile or is_tablet:
            client_info_list.append(html.Div(nick_name))
            client_info_list.append(html.Div([grid2_1, grid2_2]))
            client_info_list.append(html.Div(main_panel))
            client_info_list.append(html.Hr())

    return client_info_list

# Dash App
app = dash.Dash(__name__)

@app.callback(
    Output('client_info_container', 'children'),
    Input('store_13', 'data'),
    Input('row_data', 'data')
)
def update_client_info(store_13, row_data):
    if not row_data:
        raise PreventUpdate

    client_info_list = []
    for row in row_data:
        nick_name = row['nick_name']
        client_info_list = process_client_info(row, nick_name, client_info_list)

    return client_info_list

if __name__ == '__main__':
    app.run_server(debug=True)