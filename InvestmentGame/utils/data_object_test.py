import os
import random
import pandas as pd
import numpy as np
from InvestmentGame.utils.data_object import InvestmentData
from InvestmentGame.utils.data_prepper import DataPrepper

data_path = os.path.join("InvestmentGame", "../data")

# Load the data object
data_obj = InvestmentData("investment_data")

def test_data_query():
    # Load tickers
    tickers = InvestmentData.tickers

    # Iterating randomly X times over tickers and dates
    NUM_TICKER_TESTS = 20
    NUM_DATE_TESTS = 1000
    TOLERANCE = 1e-6

    for _ in range(NUM_TICKER_TESTS):
        ticker = random.choice(tickers)

        # Load the CSV file using the updated path
        df = pd.read_csv(os.path.join(data_path, f"{ticker}.csv"), index_col="Date", parse_dates=True)

        print(df)

        for _ in range(NUM_DATE_TESTS):
            date = random.choice(df.index)

            # Querying the data object
            price_obj, volume_obj = data_obj.query(date, ticker)
            price_csv, volume_csv = df.loc[date, ["Adj Close", "Volume"]]

            # Handling NaNs
            if pd.isna(price_csv) or pd.isna(volume_obj):
                continue

            # Assertions with tolerance
            assert np.isclose(price_obj, price_csv,
                              atol=TOLERANCE), f"Expected {price_csv}, but got {price_obj} for {ticker} on {date}."
            assert np.isclose(volume_obj, volume_csv,
                              atol=TOLERANCE), f"Expected {volume_csv}, but got {volume_obj} for {ticker} on {date}."

if __name__ == "__main__":
    test_data_query()