import os
from pathlib import Path
import pandas as pd
from models.models import print_current_step
import plotly.graph_objects as go
from dash import Dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc


class ChartMaker:
    """
    Class for loading all datasources and creating the charts
    to be returned within the dashboard view
    """

    def __init__(self):
        self.source_files_dir = os.path.join(Path(os.path.abspath(__file__)).parent.parent, 'datasource')
        self.source_files = [
            {
                'aggr_type': 'mean',
                'file_name': 'trip_date_mean.csv',
                'df': pd.DataFrame()
            }, {
                'aggr_type': 'median',
                'file_name': 'trip_date_median.csv',
                'df': pd.DataFrame()
            }
        ]
        self._run()

    def _load_dataframes(self):
        """
        Loads the dataframes
        """
        print_current_step('loading dataframes')
        # load each file
        for file in self.source_files:
            file['df'] = pd.read_csv(self.source_files_dir + '\\' + file['file_name'])
            # format trip_date to date
            file['df']['trip_date'] = pd.to_datetime(file['df']['trip_date'], format='%Y-%m-%d')

    def fares_chart(self, logarithmic_scale_y_axes=False):
        """
        Creates the prices trends chart
        """
        # list of figures
        figs = []
        # iterate over the mean/median dataframes
        for file in self.source_files:
            df = file['df']
            for col in df.columns:
                if col != 'trip_date':
                    figs.append(
                        go.Scatter(
                            x=df['trip_date'],
                            y=df[col],
                            mode='lines',
                            name=(file['aggr_type'] + ' ' + col.replace('_', ' ')).title()
                        )
                    )

        # figure to be returned
        fig = go.Figure(data=figs)
        # update the x_axes so absent dates (like 2019-01 and 2020-01)
        # don't have large gaps where dates are absent
        # any df referenced before assignment error will not cause a problem
        # because the same date ranges exist in all files, their only difference
        # is the type of aggregation occurred
        dt_all = pd.date_range(start=df['trip_date'].iloc[0], end=df['trip_date'].iloc[-1])
        dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df['trip_date'])]
        dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]
        fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])
        # update yaxis to return chart type
        fig.update_yaxes(type='log' if logarithmic_scale_y_axes is True else 'linear')
        # set hovermode to x axis
        fig.update_layout(hovermode='x')
        return fig

    def tips_chart(self, logarithmic_scale_y_axes=False):
        """
        Creates the tips trends chart
        """
        # list of figures
        figs = []
        # iterate over the mean/median dataframes
        for file in self.source_files:
            df = file['df']
            figs.append(
                go.Scatter(
                    x=df['fare_amount'],
                    y=df['tip_amount'],
                    mode='markers',
                    name=file['aggr_type'].title() + ' Fares & Tips',
                    hovertext=f"fare, tip"
                )
            )

        # figure to be returned
        fig = go.Figure(data=figs)
        # update the x_axes so absent dates (like 2019-01 and 2020-01)
        # don't have large gaps where dates are absent
        # any df referenced before assignment error will not cause a problem
        # because the same date ranges exist in all files, their only difference
        # is the type of aggregation occurred
        dt_all = pd.date_range(start=df['trip_date'].iloc[0], end=df['trip_date'].iloc[-1])
        dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df['trip_date'])]
        dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]
        fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])
        # update yaxis to return chart type
        fig.update_yaxes(type='log' if logarithmic_scale_y_axes is True else 'linear')
        # primarily a marker chart so hovermode set to nearest
        fig.update_layout(hovermode='closest')
        return fig

    def _run(self):
        self._load_dataframes()


def protect_views(app, login_required):
    """
    Takes in app and flask.login_required then protects the
    url_base_pathname as a protected route to ensure only
    authenticated users can access the dashboard
    """
    for view_func in app.server.view_functions:
        if view_func.startswith(app.config["url_base_pathname"]):
            app.server.view_functions[view_func] = login_required(app.server.view_functions[view_func])
    return app


def initiate_dash_app():
    """
    Core dash app / dashboard view
    """
    # ChartMaker class to load all dataframes and create the necessary figures
    charts = ChartMaker()
    app = Dash(__name__, server=False, url_base_pathname='/dashboard/')
    app.layout = html.Div([
        html.H1('Dashboard home'),
        dcc.Graph(
            id='chart_fares',
            figure=charts.fares_chart(logarithmic_scale_y_axes=True)
        ),
        dcc.Graph(
            id='chart_tips',
            figure=charts.tips_chart(logarithmic_scale_y_axes=True)
        )
    ])

    return app
