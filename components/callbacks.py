from dash.dependencies import Input, Output, State
from datetime import datetime
from utils.data_fetcher import fetch_all_data
from concurrent.futures import ThreadPoolExecutor
from dash import html, dash_table
from config.tickers import TICKERS_CONFIG


def create_unified_table(all_data, tickers_config):
    all_rows = []
    numeric_columns = ['change', 'ref_return', 'weekly_return', 'monthly_return', 
                      'quarterly_return', 'monthly_correlation', 'quarterly_correlation',
                      'monthly_beta', 'quarterly_beta', 'weekly_iv', 
                      'monthly_iv', 'quarterly_iv', 'realized_vol', 'vol_premium']
    
    # Define which columns should have color gradients
    return_columns = [
        'change', 'ref_return', 'weekly_return', 'monthly_return', 'quarterly_return'
    ]
    
    iv_columns = [
        'weekly_iv', 'monthly_iv', 'quarterly_iv', 'vol_premium'
    ]
    
    def cividis_color(normalized):
        """Returns a color from cividis colormap - dark blue to yellow"""
        if normalized < 0.25:
            return f'rgba(0, 32, 81, {max(0.2, normalized * 4):.2f})'    # Dark blue
        elif normalized < 0.5:
            return f'rgba(43, 77, 111, {max(0.2, normalized * 2):.2f})'  # Blue
        elif normalized < 0.75:
            return f'rgba(146, 126, 80, {max(0.2, normalized * 1.5):.2f})'  # Tan
        else:
            return f'rgba(251, 230, 29, {max(0.2, normalized):.2f})'  # Yellow

    def red_green_color(val, normalized):
        """Returns a red-green color based on value"""
        if val < 0:
            opacity = abs(normalized - 0.5) * 2
            return f'rgba(255, 0, 0, {max(0.2, opacity):.2f})'
        else:
            opacity = normalized
            return f'rgba(42, 157, 143, {max(0.2, opacity):.2f})'  # #2A9D8F with opacity

    # Collect numeric values and format data
    for category, tickers in tickers_config.items():
        all_rows.append({
            'ticker': category,
            'is_group_header': True,
            **{col: '' for col in ['last'] + numeric_columns}
        })
        
        for ticker in tickers:
            if ticker in all_data:
                data = all_data[ticker]
                formatted_data = {
                    'ticker': ticker,
                    'is_group_header': False,
                    'last': f"${data['last']:.2f}",
                }
                
                for col in numeric_columns:
                    val = data.get(col)
                    if isinstance(val, (int, float)) and not isinstance(val, bool):
                        if col in ['change', 'ref_return', 'weekly_return', 'monthly_return', 'quarterly_return']:
                            formatted_data[col] = f"{val:.2f}%"
                        elif ((col.endswith('_iv')) | ('vol' in col)):
                            formatted_data[col] = f"{val:.1f}%"
                        else:
                            formatted_data[col] = f"{val:.2f}"
                    else:
                        formatted_data[col] = "N/A"
                
                all_rows.append(formatted_data)

    # Create color styles for each column
    style_data_conditional = [
        {
            'if': {'filter_query': '{is_group_header} eq True'},
            'backgroundColor': '#264653',  # Dark blue background for headers
            'color': 'white',
            'fontWeight': '600',
            'fontSize': '13px'
        }
    ]

    # Create color gradients for specified columns only
    for col in numeric_columns:
        if col in return_columns or col in iv_columns:
            numeric_values = []
            for row in all_rows:
                if not row['is_group_header'] and row[col] != 'N/A':
                    try:
                        val = float(str(row[col]).replace('%', '').replace('$', ''))
                        numeric_values.append(val)
                    except ValueError:
                        continue

            if numeric_values:
                min_val, max_val = min(numeric_values), max(numeric_values)
                range_val = max_val - min_val
                
                if range_val != 0:
                    for val in numeric_values:
                        normalized = (val - min_val) / range_val
                        
                        # Format the value as it appears in the table for matching
                        if col in return_columns:
                            formatted_val = f"{val:.2f}%"
                            color = red_green_color(val, normalized)
                        elif col in iv_columns:
                            formatted_val = f"{val:.1f}%"
                            color = cividis_color(normalized)  # Use cividis for IV
                        
                        style = {
                            'if': {
                                'filter_query': f'{{{col}}} = "{formatted_val}"',
                                'column_id': col
                            },
                            'backgroundColor': color
                        }
                        style_data_conditional.append(style)

    return dash_table.DataTable(
        data=all_rows,
        columns=[
            {'name': '', 'id': 'ticker'},
            {'name': 'last', 'id': 'last'},
            {'name': 'change', 'id': 'change'},
            {'name': 'ref_return', 'id': 'ref_return'},
            {'name': '1wk ret', 'id': 'weekly_return'},
            {'name': '1month return', 'id': 'monthly_return'},
            {'name': '1qtr return', 'id': 'quarterly_return'},
            {'name': '1month corr', 'id': 'monthly_correlation'},
            {'name': '1qtr corr', 'id': 'quarterly_correlation'},
            {'name': '1month beta', 'id': 'monthly_beta'},
            {'name': '1qtr beta', 'id': 'quarterly_beta'},
            {'name': 'weekly IV', 'id': 'weekly_iv'},
            {'name': 'monthly IV', 'id': 'monthly_iv'},
            {'name': 'quarterly IV', 'id': 'quarterly_iv'},
            {'name': 'realized vol(20D)', 'id': 'realized_vol'},
            {'name': 'vol premium(MonthlyIV/RealVol)', 'id': 'vol_premium'},
            
        ],
        style_header={
            'backgroundColor': '#000066',
            'color': 'white',
            'fontWeight': '600',
            'fontSize': '11px',
            'fontFamily': 'monospace',
            'border': '1px solid #0a0a2a',
            'padding': '8px 15px'
        },
        style_cell={
            'backgroundColor': 'white',
            'color': 'black',
            'fontSize': '11px',
            'fontFamily': 'monospace',
            'border': '1px solid #e2e8f0',
            'padding': '8px 10px',
            'textAlign': 'right',
            'height': '25px'
        },
        style_cell_conditional=[
            {
                'if': {'column_id': 'ticker'},
                'textAlign': 'left',
                'fontWeight': '500'
            }
        ],
        style_data_conditional=style_data_conditional,
        style_table={
            'borderCollapse': 'collapse',
            'borderSpacing': '0',
            'width': '100%'
        }
    )


            
def init_callbacks(app):
    @app.callback(
        [Output('personal-tickers-store', 'data'),
         Output('ticker-input', 'value')],
        [Input('add-ticker-button', 'n_clicks')],
        [State('ticker-input', 'value'),
         State('personal-tickers-store', 'data')],
        prevent_initial_call=True
    )
    def update_personal_tickers(n_clicks, value, existing_tickers):
        if not value:
            return existing_tickers, ''
        
        new_tickers = [t.strip().upper() for t in value.split(',')]
        updated_tickers = list(set(existing_tickers + new_tickers))
        return updated_tickers, ''

    # Update the callback to use the new unified table
    @app.callback(
        [Output('tables-container', 'children'),
         Output('last-update-time', 'children')],
        [Input('interval-component', 'n_intervals'),
         Input('reference-date', 'date'),
         Input('personal-tickers-store', 'data')]
    )
    def update_data(_n_intervals, reference_date, personal_tickers):
        if reference_date:
            reference_date = datetime.strptime(reference_date.split('T')[0], '%Y-%m-%d')
        
        tickers_config = TICKERS_CONFIG.copy()
        if personal_tickers:
            tickers_config['My Portfolio'] = personal_tickers
        
        all_data = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for category, tickers in tickers_config.items():
                for ticker in tickers:
                    futures.append(executor.submit(fetch_all_data, ticker, reference_date))
            
            for future in futures:
                result = future.result()
                if result:
                    all_data[result['ticker']] = result
    
        table = create_unified_table(all_data, tickers_config)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return html.Div([table], style={'padding': '20px 0'}), f'Last updated: {current_time}'

    return app