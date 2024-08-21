import dash
from dash import html, dcc


dash.register_page(__name__)

# Login screen
layout = html.Form(
    [
        html.H2("请登录：", id="h1"),
        dcc.Input(placeholder="请输入用户名或电邮", type="text", id="uname-box", name='username'),
        dcc.Input(placeholder="请输入密码", type="password", id="pwd-box", name='password'),
        html.Button(children="登录", n_clicks=0, type="submit", id="login-button"),
        html.Div(children="", id="output-state")
    ], method='POST'
)
