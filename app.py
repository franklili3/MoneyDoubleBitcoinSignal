#import dash
from dash import Dash, html, dcc, page_container
#import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from utils.login_handler import restricted_page
import dash
from dash import dcc, html, Input, Output, ALL
import os
from flask import Flask, request, redirect, session
from flask_login import login_user, LoginManager, UserMixin, current_user
import requests, json
from logging.handlers import RotatingFileHandler
import logging
# Initialize the app - incorporate a Dash Bootstrap theme

#external_stylesheets = [dbc.themes.SUPERHERO]
# external JavaScript files
#external_scripts = [
#        'https://unpkg.com/dash_tvlwc@0.1.2/dash_tvlwc/dash_tvlwc.min.js'
#]

# Exposing the Flask Server to enable configuring it for logging in
server = Flask(__name__)

# 创建FileHandler，并添加到logger.handlers列表
logger = logging.getLogger(__name__)
handler = logging.FileHandler('error.log')
logger.setLevel(logging.DEBUG)#)INFO
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
handler.setFormatter(formatter)  
logger.addHandler(handler)

@server.route('/login', methods=['POST'])
def login_button_click():
    if request.form:
        username = request.form['username']
        session['username'] = username
        password = request.form['password']
        home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'
        auth_path = '/api/collections/clients/auth-with-password'
        auth_url = home_url + auth_path
       # json.dumps 将python数据结构转换为JSON
        data1 = json.dumps({"identity": username, "password": password})
        # Content-Type 请求的HTTP内容类型 application/json 将数据已json形式发给服务器
        header1 = {"Content-Type": "application/json"}
        response1 = requests.post(auth_url, data=data1, headers=header1)
        response1_status_code = response1.status_code
        response1_json = response1.json()
        response1_str = str(response1_json)
        #print('html: ', html)
        #print('response1_str: {}'.format(response1_str))
        logger.debug('response1_str: {}'.format(response1_str[0:100]))
        if response1_status_code == 400:
            return """无效的用户名或密码，请 <a href='/login'>登录</a>"""
        elif response1_status_code == 200:
            login_user(User(username))
            if 'url' in session:
                if session['url']:
                    url = session['url']
                    session['url'] = None
                    return redirect(url) ## redirect to target url
            return redirect('/home-client') ## redirect to home
        #return """无效的用户名或密码，请 <a href='/login'>登录</a>"""
'''
@server.route('/', methods=['POST'])
def access_home():
    home_url = 'https://pocketbase-5umc.onrender.com' #'http://127.0.0.1:8090/'
    auth_path = '/api/admins/auth-with-password'
    auth_url = home_url + auth_path
    username = os.environ.get('admin_username')
    logger.debug('admin_username: ', username)
    #app1.logger.debug('admin_username: {}'.format(username))
    password = os.environ.get('admin_password')
    # json.dumps 将python数据结构转换为JSON
    data1 = json.dumps({"identity": username, "password": password})
    # Content-Type 请求的HTTP内容类型 application/json 将数据已json形式发给服务器
    header1 = {"Content-Type": "application/json"}
    response1 = requests.post(auth_url, data=data1, headers=header1)
    response1_json = response1.json()
    #response1_str = str(response1_json)
    #print('html: ', html)
    #app1.logger.debug('response1_str: {}'.format(response1_str[0:100]))
    # html.json JSON 响应内容，提取token值
    if response1_json['token']:
        token = response1_json['token']
        session['token'] = token
        logger.debug('save token: {}'.format(token))
    return
'''
app = Dash(__name__, 
            title="钱翻一番",
            update_title="更新中",
            use_pages=True,
            serve_locally=True,
            include_assets_files=False,
            server=server,
            suppress_callback_exceptions=True
)#, external_stylesheets=external_stylesheets)external_scripts=external_scripts

server = app.server

# Updating the Flask Server configuration with Secret Key to encrypt the user session cookie
server.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


class User(UserMixin):
    # User data model. It has to have at least self.id as a minimum
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    """This function loads the user by user id. Typically this looks up the user from a user database.
    We won't be registering or looking up users in this example, since we'll just login using LDAP server.
    So we'll simply return a User object with the passed in username.
    """
    return User(username)

app.layout = html.Div([
                html.H1('钱翻一番投资驾驶舱'),
                dcc.Location(id="url"),
                html.Div(id="user-status-header"),
                page_container
]) 


@app.callback(
    Output("user-status-header", "children"),
    Output('url','pathname'),
    Input("url", "pathname"),
    Input({'index': ALL, 'type':'redirect'}, 'n_intervals')
)
def update_authentication_status(path, n):
    ### logout redirect
    if n:
        if not n[0]:
            return '', dash.no_update
        else:
            return '', '/login'

    ### test if user is logged in
    if current_user.is_authenticated:
        if path == '/login':
            return dcc.Link("退出", href="/logout"), '/'
        return dcc.Link("退出", href="/logout"), dash.no_update
    else:
        ### if page is restricted, redirect to login and save path
        if path in restricted_page:
            session['url'] = path
            return dcc.Link("登录", href="/login"), '/login'

    ### if path not login and logout display login link
    if current_user and path not in ['/login', '/logout']:
        return dcc.Link("登录", href="/login"), dash.no_update

    ### if path login and logout hide links
    if path in ['/login', '/logout']:
        return '', dash.no_update

if __name__ == '__main__':
    app.run(debug=True)
