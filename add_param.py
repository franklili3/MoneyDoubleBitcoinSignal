import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

app = dash.Dash(__name__)

# 示例数据
cases = [
    {"id": 1, "user_id": 1, "content": "User 1's case"},
    {"id": 2, "user_id": 2, "content": "User 2's case"},
    {"id": 3, "user_id": 3, "content": "User 3's case"}
]

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='case-content')
])

@app.callback(
    Output('case-content', 'children'),
    [Input('url', 'search')]
)
def update_case_content(search):
    # 从URL中提取id参数
    import urllib.parse
    params = urllib.parse.parse_qs(urllib.parse.urlparse(search).query)
    user_id = params.get('id', [None])[0]

    if user_id:
        user_id = int(user_id)
        for case in cases:
            if case['user_id'] == user_id:
                return html.Div(f"Case for User {user_id}: {case['content']}")

    return html.Div("No specific user case found.")

if __name__ == '__main__':
    app.run_server(debug=True)