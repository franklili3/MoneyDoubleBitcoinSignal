import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.SUPERHERO]
app = Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets)
server = app.server
app.layout = dbc.Container([
    dbc.Row([
        html.Div([
            html.H1('翻一番比特币投资驾驶舱')
        ])
    ]),
    dbc.Row([
        html.Div([
            html.Div([
                html.Div(
                    dcc.Link(f"{page['name']}", href=page["relative_path"])# - {page['path']}
                ) for page in dash.page_registry.values()
            ]),            
        ]),
        dash.page_container
    ])
])

if __name__ == '__main__':
    app.run(debug=True)