# -*- coding: utf-8 -*-

# app.py
import dash
from components.layout import create_header
from components.callbacks import init_callbacks
from config.settings import COLORS
from dash import html, dcc

def create_app():
    app = dash.Dash(__name__)
    
    app.layout = html.Div(
        style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'padding': '20px', 'font':'monospace'},
        children=[
            create_header(),
            dcc.Store(id='personal-tickers-store', data=[], storage_type='local'),  # Use local storage
            dcc.Loading(
                id="loading-1",
                type="default",
                children=html.Div(id='tables-container')
            ),
            dcc.Interval(
                id='interval-component',
                interval=300000,  # 5 minutes
                n_intervals=0
            )
        ]
    )
    
    init_callbacks(app)
    return app

# Create the app instance
app = create_app()

# This is needed for Gunicorn/Render
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)