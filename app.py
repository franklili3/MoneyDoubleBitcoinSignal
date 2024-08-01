import dash
from dash import Dash, html, dcc
#import dash_bootstrap_components as dbc
import dash_auth
import os, json


username_password_str = os.environ.get('username_password_dict')
#username_password_json = username_password_str.json()
VALID_USERNAME_PASSWORD_PAIRS =json.loads(username_password_str)
# Initialize the app - incorporate a Dash Bootstrap theme
#external_stylesheets = [dbc.themes.SUPERHERO]

app = Dash(__name__, use_pages=True)#, external_stylesheets=external_stylesheets)
server = app.server
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

app.layout = html.Div([
                html.H1('翻一番比特币投资驾驶舱'),
                html.Div([
                    html.Div([
                        html.Div(
                            dcc.Link(f"{page['name']}", href=page["relative_path"])# - {page['path']}
                        ) for page in dash.page_registry.values()
                    ]),            
                ]),
                dash.page_container
]) 


if __name__ == '__main__':
    app.run(debug=False)