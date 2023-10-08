import os
import random
import pandas as pd
import numpy as np
from tqdm import trange

from utils.data_object import InvestmentData

# Load the data object
data_obj = InvestmentData("investment_data")
data_obj = data_obj.load()

def test_data_query():
    # Load tickers
    tickers = data_obj.tickers

    # Iterating randomly X times over tickers and dates
    NUM_TICKER_TESTS = 50
    NUM_DATE_TESTS = 2000
    TOLERANCE = 1e-8

    for _ in trange(NUM_TICKER_TESTS):
        ticker = random.choice(tickers)

        # Load the CSV file using the updated path
        df = pd.read_csv(os.path.join("data", f"{ticker}.csv"), index_col="Date", parse_dates=True)

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

        print(f"Ticker {ticker} passed {NUM_DATE_TESTS} date tests.")

if __name__ == "__main__":
    test_data_query()