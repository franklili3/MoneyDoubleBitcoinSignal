#import dash
from dash import Dash, html, dcc, page_container, page_registry
#import dash_bootstrap_components as dbc

# Initialize the app - incorporate a Dash Bootstrap theme

#external_stylesheets = [dbc.themes.SUPERHERO]
# external JavaScript files
#external_scripts = [
#        'https://unpkg.com/dash_tvlwc@0.1.2/dash_tvlwc/dash_tvlwc.min.js'
#]

app = Dash(__name__, 
            title="钱翻一番",
            update_title="更新中",
            use_pages=True,
            serve_locally=False,
            include_assets_files=False
)#, external_stylesheets=external_stylesheets)external_scripts=external_scripts
server = app.server
app.layout = html.Div([
                html.H1('钱翻一番投资驾驶舱'),
                html.Div([
                    html.Div([
                        html.Div(
                            dcc.Link(f"{page['name']}", href=page["relative_path"])# - {page['path']}
                        ) for page in page_registry.values()
                    ]),            
                ]),
                page_container
]) 


if __name__ == '__main__':
    app.run(debug=False)