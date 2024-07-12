from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
#import functool
from flask_caching import Cache

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = Dash(__name__)
server = app.server
app.layout = [
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

TIMEOUT = 60 * 60 * 24
#@functools.lru_cache(maxsize=32)
@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
@cache.memoize(timeout=TIMEOUT)
def update_graph(value):
    dff = df[df.country==value]
    return px.line(dff, x='year', y='pop')

if __name__ == '__main__':
    app.run(debug=False)
