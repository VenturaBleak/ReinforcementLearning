import os
import numpy as np
import pickle


class InvestmentData:
    def __init__(self):
        self.filepath = os.path.join(os.getcwd(), "data", "investment_data.pkl")
        self.ticker_to_idx = {}
        self.date_to_idx = {}
        self.data_array = None
        self.metadata = None

        # Defining axes names
        self.axes_names = {
            0: 'Date',
            1: 'Ticker',
            2: 'Attributes'
        }

        # Defining the attributes (values) stored in the third dimension
        self.attributes = {
            0: 'Price',
            1: 'Volume'
        }

    def initial_save(self, dataframe, metadata):
        tickers = dataframe['Ticker'].unique()
        dates = dataframe.index.unique()

        # Construct Mapping Dictionaries
        self.ticker_to_idx = {ticker: i for i, ticker in enumerate(tickers)}
        self.date_to_idx = {date: i for i, date in enumerate(dates)}

        # Constructing the 3D numpy array
        num_dates = len(dates)
        num_tickers = len(tickers)
        self.data_array = np.zeros((num_dates, num_tickers, 2), dtype=np.float64)

        for idx, row in dataframe.iterrows():
            date_idx = self.date_to_idx[idx]
            ticker_idx = self.ticker_to_idx[row['Ticker']]
            self.data_array[date_idx, ticker_idx, 0] = row['Price']
            self.data_array[date_idx, ticker_idx, 1] = row['Volume']

        # Save Metadata
        self.metadata = metadata

        self.save()

    def query(self, date, ticker):
        date_idx = self.date_to_idx.get(date, -1)
        ticker_idx = self.ticker_to_idx.get(ticker, -1)
        if date_idx == -1 or ticker_idx == -1:
            raise ValueError("Date or Ticker not found in data.")
        return self.data_array[date_idx, ticker_idx, :]

    def query_metadata(self, ticker):
        return self.metadata[self.metadata['Symbol'] == ticker]

    def save(self):
        with open(self.filepath, 'wb') as f:
            pickle.dump(self, f)

    def load(self):
        with open(self.filepath, 'rb') as f:
            loaded_data = pickle.load(f)
        return loaded_data