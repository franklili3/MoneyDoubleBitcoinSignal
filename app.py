import dash
from dash import Dash, html, dcc

#import logging
#from flask_caching import Cache
#from logging.handlers import RotatingFileHandler




app = Dash(__name__, use_pages=True)
server = app.server
'''
# 创建RotatingFileHandler，并添加到app.logger.handlers列表
handler = RotatingFileHandler('error.log', maxBytes=100000, backupCount=10)
handler.setLevel(logging.INFO)#)DEBUG
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
handler.setFormatter(formatter)  

# 配置日志等级
app.logger.setLevel(logging.INFO)#)DEBUG

app.logger.addHandler(handler)
if 'REDIS_URL' in os.environ:
    
    # Use Redis if REDIS_URL set as an env variable
    cache = Cache(app.server, config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
    })
else:
    pass
    # Diskcache for non-production apps when developing locally
    cache = Cache(app.server, config={
        'CACHE_TYPE': 'filesystem',
        'CACHE_DIR': 'cache-directory'
    })

TIMEOUT = 60 * 60 * 24
@cache.memoize(timeout=TIMEOUT)
'''
app.layout = html.Div([
    html.H1('翻一番比特币交易驾驶舱'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']}", href=page["relative_path"])# - {page['path']}
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)