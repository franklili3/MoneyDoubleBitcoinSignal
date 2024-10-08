import dash
from dash import html, dcc
from flask_login import logout_user, current_user

dash.register_page(__name__,
                   title="钱翻一番-退出")


def layout(**kwargs):
    if current_user.is_authenticated:
        logout_user()
    return html.Div(
        [
            html.Div(html.H2("您已经退出，将访问登录页")),
            dcc.Interval(id={'index':'redirectLogin', 'type':'redirect'}, n_intervals=0, interval=1*3000)
        ]
    )
