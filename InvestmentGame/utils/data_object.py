import os
import numpy as np
import pickle

class InvestmentData:
    def __init__(self, filename, test=False):
        # placeholder variables
        self.ticker_to_idx = {}
        self.date_to_idx = {}
        self.data_array = None
        self.metadata = None

        # filename & filepath
        self.filename = filename
        self.filepath = os.path.join(os.getcwd(), "data", f"{self.filename}.pkl")

        # Defining axes names, of the 3D numpy array
        self.axes_names = {
            0: 'Date',
            1: 'Ticker',
            2: 'Attributes'
        }

        # Defining the attributes (values) stored in the third dimension
        self.attributes = {
            0: 'Price',
            1: 'Volume',
            2: 'Timestep Return',
            3: 'Balance',
            4: 'Profit/Loss',
            5: 'Annualized Return',
            6: 'Daily Variance'
        }

    def initial_save(self, dataframe, metadata, period_length):
        """Populates the data object with data and metadata and saves it to a pickle file.

        Args:
            dataframe (pandas.DataFrame): The dataframe to save.
            metadata (pandas.DataFrame): The metadata to save.
            period_length (int): The number of trading days in a year.

        Returns:
            None
        """

        # get tickers
        self.tickers = dataframe['Ticker'].unique()
        self.dates = dataframe.index.unique()

        # Construct Mapping Dictionaries
        self.ticker_to_idx = {ticker: i for i, ticker in enumerate(self.tickers)}
        self.date_to_idx = {date: i for i, date in enumerate(self.dates)}

        # Constructing the 3D numpy array
        num_dates = len(self.dates)
        num_tickers = len(self.tickers)

        # Increase the array dimensionality:
        self.data_array = np.zeros((num_dates, num_tickers, len(self.attributes)), dtype=np.float64)

        prev_prices = {}  # Dictionary to store the previous prices

        for idx, row in dataframe.iterrows():
            date_idx = self.date_to_idx[idx]
            ticker_idx = self.ticker_to_idx[row['Ticker']]

            # 0: 'Price',
            self.data_array[date_idx, ticker_idx, 0] = row['Price']

            # 1: 'Volume',
            self.data_array[date_idx, ticker_idx, 1] = row['Volume']

            # 2: 'Timestep Return'
            if row['Ticker'] == "FED":
                daily_return = (1 + row['Price'] / 100) ** (1 / period_length) - 1
            else:
                daily_return = (row['Price'] - prev_prices.get(row['Ticker'], row['Price'])) / prev_prices.get(row['Ticker'], row['Price'])
            self.data_array[date_idx, ticker_idx, 2] = daily_return
            prev_prices[row['Ticker']] = row['Price']

            # 3: 'Balance',
            # Let's use the initial starting balance (zero) and compound it with the timestep return.
            self.data_array[date_idx, ticker_idx, 3] = self.data_array[date_idx - 1, ticker_idx, 3] * (1 + daily_return) if date_idx > 0 else 0

            # 4: 'Profit/Loss',
            # Initialized as zeros, will be populated later in the simulation backbone
            self.data_array[date_idx, ticker_idx, 4] = 0

            # 5: 'Annualized Return'
            # If the current date index is greater than period length, calculate the rolling mean
            if date_idx >= period_length:
                self.data_array[date_idx, ticker_idx, 5] = (1 + np.mean(self.data_array[date_idx-period_length:date_idx, ticker_idx, 2])) ** period_length - 1

            # 6: 'Daily Variance'
            # If the current date index is greater than period length, calculate the rolling variance
            if date_idx >= period_length:
                self.data_array[date_idx, ticker_idx, 6] = np.std(self.data_array[date_idx-period_length:date_idx, ticker_idx, 2])

        # Save Metadata
        self.metadata = metadata

        self.save()

    def query(self, ticker, date, key):
        """Returns the value for a given date, ticker, and key.

        Args:
            date (datetime): Date to query.
            ticker (str): Ticker to query.
            key (str): Attribute key to query (e.g., "Price", "Volume").

        Returns:
            float: Value for the given date, ticker, and key.
        """
        date_idx = self.date_to_idx.get(date, -1)
        ticker_idx = self.ticker_to_idx.get(ticker, -1)
        attribute_idx = list(self.attributes.values()).index(key) if key in self.attributes.values() else -1

        if date_idx == -1 or ticker_idx == -1 or attribute_idx == -1:
            raise ValueError(f"Date {date_idx}, Ticker {ticker_idx}, or Attribute Key {attribute_idx} not found in data.")

        return self.data_array[date_idx, ticker_idx, attribute_idx]

    def save(self):
        with open(self.filepath, 'wb') as f:
            pickle.dump(self, f)

    def load(self):
        with open(self.filepath, 'rb') as f:
            loaded_data = pickle.load(f)
            print(f"DataObject successfully loaded from: {self.filepath}")
        return loaded_data