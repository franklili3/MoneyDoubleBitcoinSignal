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

# 设置应用布局，包括URL组件和内容显示区域
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # URL导航组件，用于监听URL变化
    html.Div(id='case-content')  # 内容容器，根据URL显示不同内容
])

@app.callback(
    Output('case-content', 'children'),  # 1. 输出：更新case-content的子元素
    [Input('url', 'search')]  # 2. 输入：当URL的查询参数变化时触发回调
)
def update_case_content(search):
    """
    根据URL中的查询参数更新用户案例内容。

    参数:
    - search: URL的查询部分，用于提取查询参数。

    返回:
    - 根据用户ID找到的案例内容，或者返回未找到的提示信息。
    """
    # 从URL中提取id参数
    import urllib.parse
    params = urllib.parse.parse_qs(urllib.parse.urlparse(search).query)
    user_id = params.get('id', [None])[0]

    # 如果提取到了有效的用户ID
    if user_id:
        user_id = int(user_id)
        # 遍历预定义的案例列表，寻找匹配用户ID的案例
        for case in cases:
            if case['user_id'] == user_id:
                return html.Div(f"Case for User {user_id}: {case['content']}")

    # 如果没有找到匹配的案例，返回提示信息
    return html.Div("No specific user case found.")

if __name__ == '__main__':
    app.run_server(debug=True)  # 启动Dash应用服务器，开启调试模式