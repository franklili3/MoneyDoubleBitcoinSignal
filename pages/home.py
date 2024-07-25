import dash
from dash import html

dash.register_page(__name__, 
    path='/',
    title='主页',
    name='主页')

layout = html.Div([
    html.H1('最新数据'),
    html.Div('比特币交易信号'),
])