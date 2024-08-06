import dash
from dash import Dash, html, dcc
#import dash_bootstrap_components as dbc

# Initialize the app - incorporate a Dash Bootstrap theme

#external_stylesheets = [dbc.themes.SUPERHERO]
# external JavaScript files
external_scripts = [
        'https://unpkg.com/dash_tvlwc@0.1.2/dash_tvlwc/dash_tvlwc.min.js'
]

app = Dash(__name__, 
            use_pages=True,
            serve_locally=False,
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