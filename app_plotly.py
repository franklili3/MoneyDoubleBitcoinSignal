from dash import Dash, html, dcc, callback, Output, Input#, DiskcacheManager, CeleryManager
import plotly.express as px
import pandas as pd
#from uuid import uuid4
import os
from flask_caching import Cache

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')


#launch_uid = uuid4()
TIMEOUT = 60 * 60 * 24
app = Dash(__name__)#, background_callback_manager=background_callback_manager)
server = app.server
if 'REDIS_URL' in os.environ:
    '''
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery
    celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    background_callback_manager = CeleryManager(
        celery_app, cache_by=[lambda: launch_uid], expire=TIMEOUT
    )'''
    cache = Cache(app.server, config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
    })
else:
    '''
    # Diskcache for non-production apps when developing locally
    import diskcache
    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(
        cache, cache_by=[lambda: launch_uid], expire=TIMEOUT
    )'''
    cache = Cache(app.server, config={
        'CACHE_TYPE': 'filesystem',
        'CACHE_DIR': 'cache-directory'
    })    
app.config.suppress_callback_exceptions = True
app.layout = [
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]




@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')#,
    #background=True
)
@cache.memoize(timeout=TIMEOUT)
def update_graph(value):
    dff = df[df.country==value]
    return px.line(dff, x='year', y='pop')

if __name__ == '__main__':
    app.run(debug=True)
