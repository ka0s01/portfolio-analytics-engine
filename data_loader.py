import yfinance as yf
import pandas as pd
import numpy as np
import  matplotlib.pyplot as plt
import pprint

def download_stock_data(ticker,start_date=None,end_date=None,period='1y'):
    if start_date and end_date:
        df = yf.download(ticker,start = start_date,end=end_date,progress=False)
    else:
        df = yf.download(ticker,period=period,progress=False)
    if(df.empty):
        raise ValueError(f"No data downloaded check ticker for {ticker}")
    print(f"downloaded {len(df)} days of data for {ticker}")
    return df

def download_multiple_stocks(tickers,start_date = None, end_date = None , period='1yr'):
    data={}
    for ticker in tickers:
        try :
            data[ticker] = yf.download_stock_data(ticker,start_date,end_date,period)
        except Exception as e:
            print(f"failed to download {ticker}: {e}")
    return data


def save_data(df,filename):
    df.to_csv(filename)

def load_data(filename):
    df = pd.read_csv(filename)
    return df



