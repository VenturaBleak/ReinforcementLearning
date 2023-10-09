import os
import quandl
import yfinance as yf
import pandas as pd
from tqdm import tqdm

class DataFetcher:
    def __init__(self, start_date="2000-01-01", end_date="2023-06-30"):
        self.start_date = start_date
        self.end_date = end_date
        if not os.path.exists(os.path.join('data')):
            os.mkdir(os.path.join('data'))

    def fetch_fed_funds_rate(self):
        api_key = os.environ.get('QUANDL_API_KEY')
        if not api_key:
            raise ValueError("Quandl API key not set in environment variables.")

        quandl.ApiConfig.api_key = api_key
        data = quandl.get("FRED/DFF", start_date=self.start_date, end_date=self.end_date)
        data.to_csv(os.path.join("data", "fed_funds_rate.csv"))

    def get_sp500_tickers(self):
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = table[0]
        tickers = df['Symbol'].tolist()
        return tickers

    def download_stock_data(self):
        tickers = self.get_sp500_tickers()
        for ticker in tqdm(tickers):
            data = yf.download(ticker, start=self.start_date, end=self.end_date)
            data.to_csv(os.path.join("data", f"{ticker}.csv"))

    def is_data_fetched(self):
        if not os.path.exists(os.path.join("data")):
            return False
        if not os.path.exists(os.path.join("data", "fed_funds_rate.csv")):
            return False
        tickers = self.get_sp500_tickers()
        for ticker in tickers:
            if not os.path.exists(os.path.join("data", f"{ticker}.csv")):
                return False
        return True

    def run(self):
        if not self.is_data_fetched():
            self.fetch_fed_funds_rate()
            self.download_stock_data()