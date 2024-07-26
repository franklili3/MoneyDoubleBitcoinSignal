import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True)
server = app.server
app.layout = html.Div([
    html.H1('翻一番比特币投资驾驶舱'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']}", href=page["relative_path"])# - {page['path']}
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=False)