import pandas as pd
import os

from .data_object import InvestmentData
import numpy as np

class DataPrepper:
    def __init__(self, period_length):
        self.period_length = period_length
        self.data_filename = "investment_data"

    def get_sp500_tickers(self):
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = table[0]
        tickers = df['Symbol'].tolist()
        return tickers

    def fetch_metadata(self, tickers):
        # Fetching metadata
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        metadata = table[0]
        metadata = metadata[metadata['Symbol'].isin(tickers)]
        return metadata

    def prepare_and_merge_data(self):
        # if data csv files don't exist
        if not os.path.exists(os.path.join("data", "data.csv")):
            # Constants
            DATE_REF_TICKER = "IBM"  # Ticker that serves as the date reference

            # Load the IBM data as it's our date reference
            ref_df = pd.read_csv(os.path.join("data", f"{DATE_REF_TICKER}.csv"), index_col="Date", parse_dates=True)
            ref_df["Ticker"] = DATE_REF_TICKER
            ref_df = ref_df[["Ticker", "Adj Close", "Volume"]]
            ref_df.rename(columns={"Adj Close": "Price"}, inplace=True)

            # Use the ref_df dataframe to reindex other stock dataframes to match its date range
            reindexer = pd.DataFrame(index=ref_df.index)

            # Create a container to store the dataframes
            all_data = [ref_df]

            # Load the Fed rate data and reindex it to match the date reference
            fund_rates = pd.read_csv(os.path.join("data", "fed_funds_rate.csv"), index_col="Date", parse_dates=True)
            fund_rates = reindexer.merge(fund_rates, left_index=True, right_index=True, how='left')
            fund_rates["Ticker"] = "FED"
            fund_rates.rename(columns={"Value": "Price"}, inplace=True)
            fund_rates["Volume"] = 0
            all_data.append(fund_rates)

            # Get the list of tickers
            tickers = self.get_sp500_tickers()
            valid_tickers = tickers.copy()

            for ticker in tickers:
                # Avoid double counting
                if ticker == DATE_REF_TICKER:
                    continue

                try:
                    df = pd.read_csv(os.path.join("data", f"{ticker}.csv"), index_col="Date", parse_dates=True)
                    df["Ticker"] = ticker
                    df = df[["Ticker", "Adj Close", "Volume"]]
                    df.rename(columns={"Adj Close": "Price"}, inplace=True)

                    # Skip tickers with all NaN values in the "Price" column
                    if df["Price"].isna().all():
                        valid_tickers.remove(ticker)
                        continue

                    # Reindex the dataframe to match the date range in ref_df
                    df = reindexer.merge(df, left_index=True, right_index=True, how='left')
                    df["Ticker"].fillna(ticker, inplace=True)

                    all_data.append(df)
                except FileNotFoundError:
                    pass

            # Concatenate the dataframes in all_data
            merged_data = pd.concat(all_data)

            # Assert the length of merged_data is as expected
            assert len(merged_data) == (len(valid_tickers) + 1) * len(ref_df)

            # Handle newly listed companies
            start_date = merged_data.index.min()
            for ticker in valid_tickers:
                ticker_data = merged_data[merged_data["Ticker"] == ticker]
                if ticker_data["Price"].head(1).isna().values[0]:
                    first_non_nan_date = ticker_data["Price"].first_valid_index()
                    condition = (merged_data["Ticker"] == ticker) & (merged_data.index < first_non_nan_date)
                    merged_data.loc[condition, ["Price", "Volume"]] = -6666.6666

            # Handle delisted companies
            end_date = merged_data.index.max()
            for ticker in valid_tickers:
                ticker_data = merged_data[merged_data["Ticker"] == ticker]
                if ticker_data["Price"].tail(1).isna().values[0]:
                    last_non_nan_date = ticker_data["Price"].last_valid_index()
                    condition = (merged_data["Ticker"] == ticker) & (merged_data.index > last_non_nan_date)
                    merged_data.loc[condition, ["Price", "Volume"]] = -5555.5555

            # Remove tickers with over 1% missing values, per ticker -> we need the number of unique dates per ticker
            threshold = 0.01 * len(merged_data.index.unique())
            for ticker in valid_tickers:
                ticker_data = merged_data[merged_data["Ticker"] == ticker]
                if ticker_data["Price"].isna().sum() > threshold:
                    merged_data = merged_data[merged_data["Ticker"] != ticker]
                    # Remove ticker from valid_tickers
                    valid_tickers.remove(ticker)

            assert (merged_data.index.unique().values == ref_df.index.unique().values).all()

            # make sure that the data is sorted by date and ticker
            merged_data.sort_values(by=["Date", "Ticker"], inplace=True)

            # Forward fill NaN values, per ticker, make sure not to spill over to other tickers
            for ticker in valid_tickers:
                ticker_data = merged_data[merged_data["Ticker"] == ticker].copy()
                ticker_data.ffill(inplace=True)
                merged_data.loc[merged_data["Ticker"] == ticker] = ticker_data

            # replace the -6666.6666 and -5555.5555 values with NaN
            merged_data.replace(-6666.6666, np.nan, inplace=True)
            merged_data.replace(-5555.5555, np.nan, inplace=True)

            # ToDO: Find more elegant way to handle NaN values!
            # for simplicty, drop all columns that include NaN values, print number of dropped tickers
            # also, remove the dropped ticker from the valid_tickers list
            dropped_tickers = []
            for ticker in valid_tickers:
                ticker_data = merged_data[merged_data["Ticker"] == ticker]
                if ticker_data.isna().any().any():
                    merged_data = merged_data[merged_data["Ticker"] != ticker]
                    dropped_tickers.append(ticker)
                    valid_tickers.remove(ticker)
            print(f"Dropped {len(dropped_tickers)} tickers due to NaN values in the data.")

            # Save the DataFrame
            merged_data.to_csv(os.path.join("data", "data.csv"))

            # assert that unique values in the "Ticker" column are the same as valid_tickers (sorted)
            assert merged_data["Ticker"].unique().tolist().sort() == valid_tickers.sort()

        else:
            merged_data = pd.read_csv(os.path.join("data", "data.csv"), index_col="Date", parse_dates=True)
            valid_tickers = merged_data["Ticker"].unique().tolist()

        # Initializing and saving data
        investment_data_obj = InvestmentData(self.data_filename)
        investment_data_obj.initial_save(merged_data, self.fetch_metadata(valid_tickers), self.period_length)

    def is_data_prepped(self):
        return os.path.exists(os.path.join("data", f"{self.data_filename}.pkl"))

    def run(self):
        if not self.is_data_prepped():
            self.prepare_and_merge_data()