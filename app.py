import dash
from dash import Dash, html, dcc
#import dash_bootstrap_components as dbc

# Initialize the app - incorporate a Dash Bootstrap theme
#external_stylesheets = [dbc.themes.SUPERHERO]
# external JavaScript files
external_scripts = [
    'https://unpkg.com/@babel/polyfill@7.12.1/dist/polyfill.min.js',
    'https://unpkg.com/dash-core-components@2.14.1/dash_core_components/dash_core_components-shared.js',
    'https://unpkg.com/dash-core-components@2.14.1/dash_core_components/dash_core_components.js',
    'https://unpkg.com/dash-daq@0.5.0/dash_daq/dash_daq.min.js',
    'https://unpkg.com/dash-html-components@2.0.18/dash_html_components/dash_html_components.min.js',
    'https://unpkg.com/dash-renderer@1.20.1/build/dash_renderer.min.js',
    'https://unpkg.com/dash-table@5.2.11/dash_table/bundle.js',
    'https://unpkg.com/prop-types@15.8.1/prop-types.min.js',
    'https://unpkg.com/react-dom@16.14.0/umd/react-dom.production.min.js',
    'https://unpkg.com/react@16.14.0/umd/react.production.min.js'
]
app = Dash(__name__, 
            use_pages=True,
            external_scripts=external_scripts
)#, external_stylesheets=external_stylesheets)
server = app.server
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