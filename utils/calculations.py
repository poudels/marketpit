# calculations.py
import numpy as np
import pandas as pd

def calculate_iv(calls_data, puts_data, spot_price, days_to_expiry):
   """Calculate IV using (c+p)/(0.8*S*sqrt(t))"""
   try:
       # Get options within 5% of spot
       merged = pd.merge(calls_data, puts_data, on='strike', suffixes=('_call', '_put'))
       merged = merged[
           (merged['strike'] >= spot_price * 0.90) &
           (merged['strike'] <= spot_price * 1.10)
       ]
       
       if merged.empty:
           return None
           
       # Find strike with minimum c-p difference
       merged['cp_diff'] = abs(merged['lastPrice_call'] - merged['lastPrice_put'])
       best_match = merged.loc[merged['cp_diff'].idxmin()]
       
       # Calculate IV
       call_price = best_match['lastPrice_call']
       put_price = best_match['lastPrice_put']
       t = days_to_expiry / 360
       
       iv = (call_price + put_price) / (0.8 * spot_price * np.sqrt(t))
       return iv * 100  # Convert to percentage
       
   except Exception as e:
       print(f"IV calculation error: {e}")
       return None


def calculate_spy_metrics(stock_returns, spy_returns, lookback):
    """
    Calculate correlation and beta to SPY
    
    Args:
        stock_returns (pd.Series): Stock returns timeseries
        spy_returns (pd.Series): SPY returns timeseries
        lookback (int): Number of periods to look back
        
    Returns:
        tuple: (correlation, beta)
    """
    try:
        # Convert both series to timezone-naive if they aren't already
        stock_returns_naive = stock_returns.copy()
        spy_returns_naive = spy_returns.copy()
        
        if stock_returns_naive.index.tz is not None:
            stock_returns_naive.index = stock_returns_naive.index.tz_localize(None)
        if spy_returns_naive.index.tz is not None:
            spy_returns_naive.index = spy_returns_naive.index.tz_localize(None)
            
        stock_period = stock_returns_naive[-lookback:]
        spy_period = spy_returns_naive[-lookback:]
        
        # Calculate metrics
        correlation = stock_period.corr(spy_period)
        covariance = stock_period.cov(spy_period)
        variance = spy_period.var()
        beta = covariance / variance
        
        return correlation, beta
        
    except Exception as e:
        print(f"SPY metrics calculation error: {e}")
        return None, None
    
    
def calculate_realized_volatility(price_series, window=20):
   """
   Calculate realized volatility using log returns over a specified window
   
   Parameters:
   price_series: pandas Series of close prices
   window: int, number of days for calculation (default 30)
   
   Returns:
   float: annualized volatility as a percentage
   """
   try:
       # Calculate log returns
       log_returns = np.log(price_series / price_series.shift(1))
       
       # Get the most recent window of returns
       recent_returns = log_returns[-window:]
       
       # Calculate realized volatility
       realized_vol = np.sqrt(np.sum(recent_returns**2)) * np.sqrt(252/window)
       
       return realized_vol *100
       
   except Exception as e:
       print(f"Error calculating realized volatility: {e}")
       return None    
   
def calculate_vol_premium(implied_vol, realized_vol):
    """Calculate volatility risk premium as IV - RV"""
    if implied_vol is not None and realized_vol is not None:
        return implied_vol/realized_vol * 100
    return None    