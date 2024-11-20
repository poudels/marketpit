import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from .calculations import calculate_iv, calculate_spy_metrics, calculate_realized_volatility, calculate_vol_premium


def get_next_expirations(options_list):
    """
    Get next Friday, monthly and quarterly options expirations
    
    Monthly expirations are typically the third Friday of each month
    Quarterly expirations are the third Friday of March, June, September, December
    
    Args:
        options_list (list): List of expiration dates in 'YYYY-MM-DD' format
        
    Returns:
        tuple: (next_friday_exp, next_monthly_exp, next_quarterly_exp)
    """
    try:
        today = datetime.now()
        
        # Convert all dates to datetime objects
        expirations = [datetime.strptime(exp, '%Y-%m-%d') for exp in options_list]
        future_expirations = sorted([exp for exp in expirations if exp > today])
        
        if not future_expirations:
            return None, None, None

        # Get next Friday expiration
        next_exp = min(future_expirations)
        
        # Find monthly expirations (third Friday of each month)
        def is_monthly_expiration(date):
            # Check if it's a Friday
            if date.weekday() != 4:  # 4 represents Friday
                return False
            
            # Check if it's the third Friday
            first_day = date.replace(day=1)
            first_friday = first_day + timedelta(days=((4 - first_day.weekday()) % 7))
            third_friday = first_friday + timedelta(weeks=2)
            return date.date() == third_friday.date()

        # Find quarterly expirations (third Friday of Mar, Jun, Sep, Dec)
        def is_quarterly_expiration(date):
            return is_monthly_expiration(date) and date.month in [3, 6, 9, 12]

        # Get next monthly expiration
        monthly_expirations = [exp for exp in future_expirations if is_monthly_expiration(exp)]
        next_month = monthly_expirations[0] if monthly_expirations else None

        # Get next two quarterly expirations
        quarterly_expirations = [exp for exp in future_expirations if is_quarterly_expiration(exp)]
        next_quarter = quarterly_expirations[0] if quarterly_expirations else None
        
        return next_exp, next_month, next_quarter

    except Exception as e:
        print(f"Error getting expirations: {e}")
        return None, None, None
    

def fetch_all_data(ticker, reference_date):
   """Fetch and calculate all metrics for a ticker"""
   try:
       stock = yf.Ticker(ticker)
       hist = stock.history(period="1y")
       
       if hist.empty:
           return None
       
       # Convert the index to datetime64[ns] without timezone
       hist.index = hist.index.tz_localize(None)

       # Get SPY data for same period
       spy = yf.Ticker('SPY').history(period="1y")
       
       # Convert reference_date to datetime64[ns] without timezone
       ref_date = pd.Timestamp(reference_date).tz_localize(None)
       
       # Find the closest price to reference_date
       reference_price = None
       if not hist.empty:
            # Get the first available price on or after reference_date
            reference_mask = hist.index >= ref_date
            if reference_mask.any():
                reference_price = hist.loc[reference_mask, 'Close'].iloc[0]
                
       # Basic price metrics
       current_price = hist['Close'].iloc[-1]
       data = {
           'ticker': ticker,
           'last': current_price,
           'change': (current_price / hist['Close'].iloc[-2] - 1) * 100,
           'weekly_return': (current_price / hist['Close'].iloc[-5] - 1) * 100,
           'monthly_return': (current_price / hist['Close'].iloc[-21] - 1) * 100,
           'quarterly_return': (current_price / hist['Close'].iloc[-63] - 1) * 100
       }
       # Calculate reference return if reference price is available
       if reference_price is not None:
           data['ref_return'] = (current_price / reference_price - 1) * 100
       else:
           data['ref_return'] = "N/A"
     
       # Calculate SPY metrics
       stock_returns = hist['Close'].pct_change().dropna()
       spy_returns = spy['Close'].pct_change().dropna()
       
       data['monthly_correlation'], data['monthly_beta'] = calculate_spy_metrics(
           stock_returns, spy_returns, 21)
       data['quarterly_correlation'], data['quarterly_beta'] = calculate_spy_metrics(
           stock_returns, spy_returns, 63)
       
       # Calculate realized volatility
       data['realized_vol'] = calculate_realized_volatility(hist['Close'])
       
       # Get IVs for different expirations
       next_exp, next_month, next_quarter = get_next_expirations(stock.options)
       
       if next_exp:
           opt_chain = stock.option_chain(next_exp.strftime('%Y-%m-%d'))
           data['weekly_iv'] = calculate_iv(
               opt_chain.calls, opt_chain.puts, current_price, 
               (next_exp.date() - datetime.now().date()).days)
       
       if next_month:
           opt_chain = stock.option_chain(next_month.strftime('%Y-%m-%d'))
           data['monthly_iv'] = calculate_iv(
               opt_chain.calls, opt_chain.puts, current_price,
               (next_month - datetime.now()).days)
       
       if next_quarter:
           opt_chain = stock.option_chain(next_quarter.strftime('%Y-%m-%d'))
           data['quarterly_iv'] = calculate_iv(
               opt_chain.calls, opt_chain.puts, current_price,
               (next_quarter - datetime.now()).days)
      
       
       # Calculate vol premium
       data['vol_premium'] = calculate_vol_premium(data['monthly_iv'], data['realized_vol'])
       
       
       return data
       
   except Exception as e:
       print(f"Error fetching data for {ticker}: {e}")
       return None