# -*- coding: utf-8 -*-

# components/layout.py
from dash import html, dcc
from datetime import datetime, timedelta
from config.settings import COLORS


def create_header():
   return html.Div([
       # Title row
       html.H1("MarketPit",
           style={
               'color': COLORS['text'],
               'fontSize': '24px',
               'fontFamily': 'monospace',
               'fontWeight': '600',
               'margin': '0',
               'padding': '0'
           }
       ),

       # Parent div
       html.Div([
           # Left div (50%)
           html.Div([
               # First row: Date picker and label
               html.Div([
                   html.Label("Ref Date: ",
                       style={
                           'fontSize': '14px',
                           'fontFamily': 'monospace',
                           'color': '#666',
                           'marginRight': '5px',
                           'display': 'inline-block',
                           'width': '100px'
                       }
                   ),
                   html.Div(create_date_picker(),
                       style={
                           'display': 'inline-block'
                       }
                   )
               ], style={'marginBottom': '5px'}),
               
               # Second row: Ticker input and label
               html.Div([
                   html.Label("Add tickers: ",
                       style={
                           'fontSize': '14px',
                           'fontFamily': 'monospace',
                           'color': '#666',
                           'marginRight': '5px',
                           'display': 'inline-block',
                           'width': '100px'
                       }
                   ),
                   html.Div(create_ticker_input(),
                       style={
                           'display': 'inline-block'
                       }
                   )
               ], style={'marginBottom': '5px'}),

               # Third row: Note
               html.Div([
                   "This was done for fun, so will naturally lack accuracy. If you have questions, reach out to me in LinekdIn: Subash Poudel ",
               ], style={
                   'fontSize': '12px',
                   'fontFamily': 'monospace',
                   'color': '#666',
                   'marginTop': '15px'
               })
           ], style={
               'width': '50%',
               'display': 'inline-block',
               'verticalAlign': 'top'
           }),

           # Right div (50%)
           html.Div(style={
               'width': '50%',
               'display': 'inline-block',
               'verticalAlign': 'top'
           })
       ], style={
           'marginTop': '5px',
           'marginBottom': '5px'
       }),

       # Last refreshed time
       html.Div(create_update_time(),
           style={
               'fontSize': '12px',
               'fontFamily': 'monospace',
               'marginBottom': '5px'
           }
       )
   ], style={
       'padding': '10px',
       'maxWidth': '1200px'
   })

       
def create_date_picker():
    today = datetime.now()
    
    return html.Div([
        dcc.DatePickerSingle(
            id='reference-date',
            min_date_allowed=today - timedelta(days=730),
            max_date_allowed=today,
            initial_visible_month=today,
            date=today - timedelta(days=30),
            style={
                'backgroundColor': COLORS['input'],
                'color': COLORS['text'],
                'fontFamily': 'monospace',
                'fontSize': '12px',
                'width': '120px',  # Make input box smaller
                'padding': '2px',
                'border': f'1px solid {COLORS["border"]}'
            },
            display_format='YYYY-MM-DD',
            placeholder='YYYY-MM-DD'
        )
    ], style={
        'display': 'inline-block'
    })

def create_ticker_input():
   return html.Div([
       dcc.Input(
           id='ticker-input',
           type='text',
           placeholder='Enter tickers separated by commas',
           style={
               'backgroundColor': COLORS['input'],
               'color': COLORS['text'],
               'border': f'1px solid {COLORS["border"]}',
               'padding': '5px',
               'width': '300px',
               'marginRight': '10px',
               'fontSize': '12px',
               'fontFamily': 'monospace'
           }
       ),
       html.Button('Add',
           id='add-ticker-button',
           style={
               'backgroundColor': COLORS['input'],
               'color': COLORS['text'],
               'border': f'1px solid {COLORS["border"]}',
               'padding': '5px 15px',
               'fontSize': '12px',
               'fontFamily': 'monospace'
           }
       )
   ])
       
def create_update_time():
    return html.Div([
        html.Span(id='last-update-time',
            style={
                'color': COLORS['neutral'],
                'fontSize': '14px',
                'fontFamily': 'monospace',
            }
        )
    ], style={'display': 'inline-block', 'verticalAlign': 'middle'})