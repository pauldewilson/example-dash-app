from dash import Dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc


def initiate_dash_app():
    app = Dash(__name__, server=False, url_base_pathname='/dashboard/')
    app.layout = html.Div([
        html.H1('Dashboard home')
    ])

    return app


def protect_views(app, login_required):
    for view_func in app.server.view_functions:
        if view_func.startswith(app.config["url_base_pathname"]):
            app.server.view_functions[view_func] = login_required(app.server.view_functions[view_func])
    return app
