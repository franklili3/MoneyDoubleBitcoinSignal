from dash import html, dcc, callback, Input, Output, State, clientside_callback
import dash_bootstrap_components as dbc
from flask import session
import dash

dash.register_page(__name__)

layout = html.Div([
    dbc.RadioItems(
        id='share-option',
        options=[
            {'label': '公开', 'value': 'public'},
            {'label': '不公开', 'value': 'private'}
        ],
        value='private',
        inline=True
    ),
    html.Div([
        dbc.Row([
            dbc.Col("我的分享链接:", width=3),
            dbc.Col(dbc.Input(id="share-link", type="text", readonly=True), width=6),
            dbc.Col(dbc.Button("复制", id="copy-button", color="primary"), width=3)
        ], className="mt-3")
    ], id="share-link-container", style={'display': 'none'}),
    html.Div(id='share-status'),
    dcc.Store(id='client-id-store')
])

@callback(
    Output('share-status', 'children'),
    Output('share-link-container', 'style'),
    Output('share-link', 'value'),
    Output('client-id-store', 'data'),
    Input('share-option', 'value')
)
def update_share_status(share_option):
    client_id = session.get('client_id', 'unknown')
    if share_option == 'public':
        share_link = f"/case?id={client_id}"
        return "您的投资组合现在是公开的", {'display': 'block'}, share_link, {'client_id': client_id}
    else:
        return "您的投资组合现在是私密的", {'display': 'none'}, "", {'client_id': client_id}

clientside_callback(
    """
    function(n_clicks, share_link) {
        if (n_clicks > 0) {
            navigator.clipboard.writeText(share_link);
            return "链接已复制到剪贴板!";
        }
        return "";
    }
    """,
    Output("copy-button", "children"),
    Input("copy-button", "n_clicks"),
    State("share-link", "value"),
    prevent_initial_call=True
)